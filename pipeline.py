"""
pipeline.py — P95.AI Lead Engine
=================================
One-command end-to-end runner. Executes all pipeline stages in order:

  1. Normalize Sources                     (normalize_*.py)
  2. Merge & dedupe raw source CSVs        (compile_leads.py)
  3. Apply hard disqualifier filter        (prefilter.py)
  4. Quota check & gap fill                (quota_check.py)
  5. Phase 3A API enrichment               (enrich_pipeline.py)
  6. Phase 3B Intent enrichment            (enrich_3b.py)
  7. Lead scoring                          (scoring_engine.py)
  8. Personalized outreach generation      (generate_linkedin_dms.py)

Usage
-----
    python pipeline.py                        # full run
    python pipeline.py --from-stage enrich    # resume from a specific stage
    python pipeline.py --dry-run              # validate env + files, no execution
    python pipeline.py --skip-outreach        # skip email generation (faster)

Stages: normalize_apollo | normalize_linkedin | normalize_seeds | normalize_engineers | merge | prefilter | quota | enrich_apis | enrich_intent | score | outreach
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

ROOT        = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT / "scripts"
DATA_DIR    = ROOT / "data"
LOG_DIR     = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# --------------------------------------------------------------------------- #
#  Stage definitions — order matters                                           #
# --------------------------------------------------------------------------- #

STAGES = [
    {
        "id":       "normalize_apollo",
        "label":    "Normalize Apollo Source",
        "script":   "normalize_apollo.py",
        "output":   "data/raw/apollo_normalized.csv",
        "required": False,
    },
    {
        "id":       "normalize_linkedin",
        "label":    "Normalize LinkedIn Source",
        "script":   "normalize_linkedin.py",
        "output":   "data/raw/linkedin_normalized.csv",
        "required": False,
    },
    {
        "id":       "normalize_seeds",
        "label":    "Normalize Seed Lists",
        "script":   "normalize_seeds.py",
        "output":   "data/raw/seeds_normalized.csv",
        "required": False,
    },
    {
        "id":       "normalize_engineers",
        "label":    "Normalize DevTools/Engineer Sources",
        "script":   "normalize_engineer_sources.py",
        "output":   "data/raw/engineer_normalized.csv",
        "required": False,
    },
    {
        "id":       "merge",
        "label":    "Merge & Dedupe Raw Sources",
        "script":   "compile_leads.py",
        "output":   "data/raw_leads.csv",
        "required": True,
    },
    {
        "id":       "prefilter",
        "label":    "Apply Hard Disqualifier Filter",
        "script":   "prefilter.py",
        "output":   "data/raw_leads_rejected.csv",
        "required": True,
    },
    {
        "id":       "quota",
        "label":    "Quota Check & Gap Fill",
        "script":   "quota_check.py",
        "output":   "data/sourcing_qa_report.md",
        "required": False,
    },
    {
        "id":       "enrich_apis",
        "label":    "Phase 3A Enrichment (Apollo/GitHub APIs)",
        "script":   "enrich_pipeline.py",
        "output":   "data/enriched_leads.csv",
        "required": True,
    },
    {
        "id":       "enrich_intent",
        "label":    "Phase 3B Enrichment (Funding + Hiring)",
        "script":   "enrich_3b.py",
        "output":   "data/enriched_leads.csv",
        "required": True,
    },
    {
        "id":       "score",
        "label":    "Lead Scoring (9-Signal Rubric)",
        "script":   "scoring_engine.py",
        "output":   "data/scored_leads.csv",
        "required": True,
    },
    {
        "id":       "outreach",
        "label":    "Personalized Outreach Generation (LinkedIn/Email)",
        "script":   "generate_linkedin_dms.py",
        "output":   "data/phase5_outreach.csv",
        "required": False,
    },
]

STAGE_IDS = [s["id"] for s in STAGES]

# --------------------------------------------------------------------------- #
#  Colours                                                                     #
# --------------------------------------------------------------------------- #

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    DIM    = "\033[2m"

def ok(msg):    print(f"  {C.GREEN}✔{C.RESET}  {msg}")
def warn(msg):  print(f"  {C.YELLOW}⚠{C.RESET}  {msg}")
def err(msg):   print(f"  {C.RED}✘{C.RESET}  {msg}")
def info(msg):  print(f"  {C.CYAN}→{C.RESET}  {msg}")
def dim(msg):   print(f"{C.DIM}  {msg}{C.RESET}")

# --------------------------------------------------------------------------- #
#  Environment validation                                                      #
# --------------------------------------------------------------------------- #

REQUIRED_ENV = ["APOLLO_API_KEY"]
OPTIONAL_ENV = ["SERPAPI_KEY", "OPENAI_API_KEY", "GITHUB_TOKEN", "CLAY_API_KEY"]

def validate_env(dry_run=False):
    print(f"\n{C.BOLD}── Environment Check ─────────────────────────────{C.RESET}")
    all_ok = True
    for key in REQUIRED_ENV:
        val = os.getenv(key, "").strip()
        if val:
            ok(f"{key} set")
        else:
            err(f"{key} missing — required for enrichment stage")
            all_ok = False
    for key in OPTIONAL_ENV:
        val = os.getenv(key, "").strip()
        if val:
            ok(f"{key} set")
        else:
            warn(f"{key} not set (optional — some features disabled)")
    if not all_ok and not dry_run:
        print(f"\n{C.RED}  Missing required env vars. Add them to .env and retry.{C.RESET}\n")
        sys.exit(1)
    return all_ok

# --------------------------------------------------------------------------- #
#  Script runner                                                               #
# --------------------------------------------------------------------------- #

def run_script(script_path: Path, stage: dict, log_file) -> bool:
    """Run a script as a subprocess, stream output, return success bool."""
    if not script_path.exists():
        err(f"Script not found: {script_path}")
        warn("Skipping — add the script to continue")
        return False

    start = time.time()
    proc = subprocess.Popen(
        [sys.executable, str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=str(ROOT),
    )

    lines = []
    for line in proc.stdout:
        print(f"    {C.DIM}{line.rstrip()}{C.RESET}")
        lines.append(line)
        log_file.write(line)

    proc.wait()
    elapsed = time.time() - start

    if proc.returncode == 0:
        ok(f"Done in {elapsed:.1f}s")
        return True
    else:
        err(f"Failed with exit code {proc.returncode}")
        return False

# --------------------------------------------------------------------------- #
#  Main                                                                        #
# --------------------------------------------------------------------------- #

def main():
    parser = argparse.ArgumentParser(
        description="P95.AI Lead Engine — end-to-end pipeline runner"
    )
    parser.add_argument(
        "--from-stage",
        choices=STAGE_IDS,
        default=None,
        metavar="STAGE",
        help=f"Resume from a specific stage. Options: {', '.join(STAGE_IDS)}",
    )
    parser.add_argument(
        "--only-stage",
        choices=STAGE_IDS,
        default=None,
        metavar="STAGE",
        help="Run only one specific stage.",
    )
    parser.add_argument(
        "--skip-outreach",
        action="store_true",
        help="Skip outreach and A/B generation (faster re-runs).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate environment and file paths only — no scripts run.",
    )
    args = parser.parse_args()

    # Banner
    print(f"\n{C.BOLD}{C.CYAN}{'=' * 55}")
    print(f"  P95.AI Lead Engine — Pipeline Runner")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")
    print(f"{'=' * 55}{C.RESET}")

    validate_env(dry_run=args.dry_run)

    # Determine which stages to run
    stages_to_run = list(STAGES)

    if args.only_stage:
        stages_to_run = [s for s in STAGES if s["id"] == args.only_stage]
    elif args.from_stage:
        idx = STAGE_IDS.index(args.from_stage)
        stages_to_run = STAGES[idx:]

    if args.skip_outreach:
        stages_to_run = [s for s in stages_to_run if s["id"] not in ("outreach",)]

    if args.dry_run:
        print(f"\n{C.BOLD}── Dry Run — Stages that would execute ──────────{C.RESET}")
        for s in stages_to_run:
            script_path = SCRIPTS_DIR / s["script"]
            exists = "✔" if script_path.exists() else "✘ MISSING"
            print(f"  [{exists}]  {s['label']}")
        print(f"\n{C.GREEN}  Dry run complete. No scripts executed.{C.RESET}\n")
        return

    # Run stages
    log_path = LOG_DIR / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    results = []

    print(f"\n{C.BOLD}── Running {len(stages_to_run)} stage(s) ─────────────────────────{C.RESET}")

    with open(log_path, "w") as log_file:
        log_file.write(f"P95.AI Pipeline Run — {datetime.now(timezone.utc).isoformat()}\n\n")

        for i, stage in enumerate(stages_to_run, 1):
            print(f"\n{C.BOLD}[{i}/{len(stages_to_run)}] {stage['label']}{C.RESET}")
            dim(f"Script: scripts/{stage['script']}")

            script_path = SCRIPTS_DIR / stage["script"]
            success = run_script(script_path, stage, log_file)
            results.append((stage, success))

            # Check output file was produced
            output_path = ROOT / stage["output"]
            if success and not output_path.exists():
                warn(f"Expected output not found: {stage['output']}")

            if not success and stage["required"]:
                err(f"Required stage '{stage['id']}' failed — stopping pipeline.")
                break

    # Summary
    print(f"\n{C.BOLD}── Summary ───────────────────────────────────────{C.RESET}")
    passed = sum(1 for _, s in results if s)
    failed = sum(1 for _, s in results if not s)

    for stage, success in results:
        status = f"{C.GREEN}PASS{C.RESET}" if success else f"{C.RED}FAIL{C.RESET}"
        print(f"  [{status}]  {stage['label']}")

    print(f"\n  {C.GREEN}{passed} passed{C.RESET}  |  {C.RED}{failed} failed{C.RESET}")
    print(f"  Log saved → {log_path.relative_to(ROOT)}")

    # Final output locations
    if passed > 0:
        print(f"\n{C.BOLD}── Output Files ──────────────────────────────────{C.RESET}")
        for stage, success in results:
            if success:
                output_path = ROOT / stage["output"]
                if output_path.exists():
                    size_kb = output_path.stat().st_size // 1024
                    ok(f"{stage['output']}  ({size_kb} KB)")

    print(f"\n{'=' * 55}\n")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
