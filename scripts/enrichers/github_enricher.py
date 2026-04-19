"""
github_enricher.py — P95.AI Lead Engine Phase 3A
=================================================
Enriches each lead with GitHub organisation signals:
  - github_org_url          (auto-discovered if blank)
  - github_ai_repo_count    (# repos with AI/infra keywords)
  - github_stars_top_repo   (stars on most popular AI/infra repo)
  - has_kubernetes          (TRUE/FALSE)
  - has_ray_or_wandb        (TRUE/FALSE)

Strategy per lead:
  1. If github_org_url already populated → analyse it directly (fast, 5000/hr limit)
  2. Try direct org lookup: GET /orgs/{domain_slug}
  3. Fall back to GitHub Search API: GET /search/users?q={slug}+type:org  (30/min limit)
  4. Try company name first word as slug
  5. Give up and return empty signals
"""

import os
import re
import time
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# --- keyword lists (all lowercase) ---

AI_INFRA_KW = {
    "llm", "inference", "serving", "ml", "machine-learning", "deep-learning",
    "nlp", "transformer", "gpu", "model-serving", "embedding", "rag",
    "langchain", "openai", "anthropic", "vllm", "triton", "mlops",
    "kubeflow", "ray", "wandb", "torch", "tensorflow", "jax",
    "diffusion", "foundation-model", "llmops", "vector-db", "vector-store",
    "tgi", "text-generation",
}

KUBE_KW = {"kubernetes", "k8s", "helm", "kube", "kubectl", "kustomize", "argocd", "flux"}

RAY_WANDB_KW = {"ray", "wandb", "weights-biases", "raydistributed", "ray-serve"}

# Delay between NON-search API calls (5 000/hr → ~0.72/s, use 0.8s to be safe)
_FAST_DELAY = 0.8
# Delay between Search API calls (30/min → 2s, use 2.2s to be safe)
_SEARCH_DELAY = 2.2


# --------------------------------------------------------------------------- #
#  Internal helpers                                                             #
# --------------------------------------------------------------------------- #

def _get(url: str, params: dict | None = None) -> requests.Response | None:
    """GET with automatic rate-limit retry."""
    if GITHUB_TOKEN == "dummy":
        return None
    try:
        resp = requests.get(url, headers=_HEADERS, params=params, timeout=12)
        if resp.status_code == 403:
            reset = int(resp.headers.get("X-RateLimit-Reset", time.time() + 65))
            wait = max(reset - time.time() + 2, 5)
            print(f"      [RATE LIMIT] sleeping {wait:.0f}s …")
            time.sleep(wait)
            resp = requests.get(url, headers=_HEADERS, params=params, timeout=12)
        return resp
    except requests.exceptions.RequestException as exc:
        print(f"      [NETWORK ERROR] {exc}")
        return None


def _domain_slug(domain: str) -> str:
    """'stripe.com' → 'stripe',  'thoughtspot.com' → 'thoughtspot'"""
    return domain.split(".")[0].lower().strip()


def _name_slug(company_name: str) -> str:
    """'Thought Spot Inc' → 'thoughtspot'"""
    return re.sub(r"[^a-z0-9]", "", company_name.lower().split()[0]) if company_name else ""


def _text_from_repo(repo: dict) -> str:
    """Combine name + description + topics into a single searchable string."""
    name = (repo.get("name") or "").lower()
    desc = (repo.get("description") or "").lower()
    topics = " ".join(t.lower() for t in (repo.get("topics") or []))
    return f"{name} {desc} {topics}"


# --------------------------------------------------------------------------- #
#  Core discovery logic                                                         #
# --------------------------------------------------------------------------- #

def _direct_org_lookup(slug: str) -> str | None:
    """Try GET /orgs/{slug}. Returns org URL or None."""
    resp = _get(f"https://api.github.com/orgs/{slug}")
    time.sleep(_FAST_DELAY)
    if resp and resp.status_code == 200:
        data = resp.json()
        login = data.get("login", "")
        if login:
            return f"https://github.com/{login}"
    return None


def _search_for_org(query: str) -> str | None:
    """Use GitHub search to find an org. Returns best-match URL or None."""
    resp = _get(
        "https://api.github.com/search/users",
        params={"q": f"{query} type:org", "per_page": 5},
    )
    time.sleep(_SEARCH_DELAY)
    if not resp or resp.status_code != 200:
        return None
    items = resp.json().get("items", [])
    for item in items:
        login = item.get("login", "").lower()
        # Accept if query string appears in the login or vice-versa
        if query.lower() in login or login in query.lower():
            return f"https://github.com/{item['login']}"
    return None


def find_github_org(domain: str, company_name: str) -> str | None:
    """
    Multi-strategy GitHub org discovery.
    Returns the org URL (e.g. 'https://github.com/stripe') or None.
    """
    slugs = list(dict.fromkeys([_domain_slug(domain), _name_slug(company_name)]))

    # Strategy 1: direct /orgs/{slug}
    for slug in slugs:
        if slug:
            url = _direct_org_lookup(slug)
            if url:
                return url

    # Strategy 2: GitHub search (slower, rate-limited)
    for slug in slugs:
        if slug and len(slug) >= 3:
            url = _search_for_org(slug)
            if url:
                return url

    return None


# --------------------------------------------------------------------------- #
#  Repo analysis                                                                #
# --------------------------------------------------------------------------- #

def analyse_org(org_url: str) -> dict:
    """
    Fetch up to 100 repos for the given org and compute AI/infra signals.
    Returns a dict of enriched fields.
    """
    result = {
        "github_ai_repo_count": 0,
        "github_stars_top_repo": 0,
        "has_kubernetes": "FALSE",
        "has_ray_or_wandb": "FALSE",
    }

    org_name = org_url.rstrip("/").split("/")[-1]
    resp = _get(
        f"https://api.github.com/orgs/{org_name}/repos",
        params={"per_page": 100, "sort": "stars", "direction": "desc"},
    )
    time.sleep(_FAST_DELAY)

    if not resp or resp.status_code != 200:
        return result

    repos = resp.json()
    ai_count = 0
    top_stars = 0
    has_k8s = False
    has_ray = False

    for repo in repos:
        text = _text_from_repo(repo)
        stars = repo.get("stargazers_count", 0)

        if any(kw in text for kw in AI_INFRA_KW):
            ai_count += 1
            top_stars = max(top_stars, stars)

        if any(kw in text for kw in KUBE_KW):
            has_k8s = True

        if any(kw in text for kw in RAY_WANDB_KW):
            has_ray = True

    result["github_ai_repo_count"] = ai_count
    result["github_stars_top_repo"] = top_stars
    result["has_kubernetes"] = "TRUE" if has_k8s else "FALSE"
    result["has_ray_or_wandb"] = "TRUE" if has_ray else "FALSE"

    return result


# --------------------------------------------------------------------------- #
#  Public entry point                                                           #
# --------------------------------------------------------------------------- #

def enrich_lead(domain: str, company_name: str, existing_org_url: str = "") -> dict:
    """
    Main entry point called by enrich_pipeline.py for each unique domain.

    Returns a dict with fields to merge back into the dataframe:
      github_org_url, github_ai_repo_count, github_stars_top_repo,
      has_kubernetes, has_ray_or_wandb
    """
    if GITHUB_TOKEN == "dummy":
        return {}
    updates: dict = {}

    org_url = existing_org_url.strip() if existing_org_url else ""

    # Discover org if missing
    if not org_url:
        org_url = find_github_org(domain, company_name) or ""
        if org_url:
            updates["github_org_url"] = org_url

    if not org_url:
        return updates  # couldn't find org — leave fields blank

    # Analyse repos
    signals = analyse_org(org_url)
    updates.update(signals)

    return updates
