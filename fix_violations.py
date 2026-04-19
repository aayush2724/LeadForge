import pandas as pd

df = pd.read_csv('data/scored_leads.csv')

# Fix 1 — total_funding_usd: float like 16000000.0 → integer 16000000
if 'total_funding_usd' in df.columns:
    def fix_funding(val):
        if pd.isna(val) or val == '':
            return val
        try:
            return str(int(float(str(val).replace(',', '').replace('$', ''))))
        except:
            return val
    df['total_funding_usd'] = df['total_funding_usd'].apply(fix_funding)

# Fix 2 — boolean columns: Python 'True'/'False' → 'TRUE'/'FALSE'
bool_cols = [
    'uses_llm_in_prod', 'has_kubernetes', 'has_ray_or_wandb',
    'has_snowflake', 'linkedin_post_30d', 'disqualified',
    'is_hiring_ml_eng'
]
for col in bool_cols:
    if col in df.columns:
        df[col] = df[col].apply(
            lambda x: 'TRUE' if str(x).strip().lower() == 'true'
            else 'FALSE' if str(x).strip().lower() == 'false'
            else '' if pd.isna(x) or str(x).strip().lower() == 'nan'
            else x
        )

# Fix 3 — funding_stage: fix invalid values including Pre-Series A
if 'funding_stage' in df.columns:
    df['funding_stage'] = df['funding_stage'].astype(str).str.strip()
    funding_map = {
        'Venture (Round not Specified)': 'Unknown',
        'Series A': 'Unknown',
        'Series E': 'Series D',
        'Series F': 'Series D',
        'Merger / Acquisition': 'Series D',
        'Private Equity': 'Series D',
        'Other': 'Unknown',
        'Seed': 'Unknown',
        'Pre-Series A': 'Unknown',
    }
    df['funding_stage'] = df['funding_stage'].replace(funding_map)
    # Final cleanup — map anything not in VALID_STAGE to Unknown
    valid_stages = {"Series B","Series C","Series D","Bootstrapped","Unknown",""}
    df['funding_stage'] = df['funding_stage'].apply(lambda x: x if x in valid_stages else "Unknown")

# Fix 4 — geo_tier: fix invalid values including Tier 3
if 'geo_tier' in df.columns:
    df['geo_tier'] = df['geo_tier'].astype(str).str.strip()
    geo_map = {
        'Other': 'EU_UK',
        'Tier 2': 'EU_UK',
        'Tier 3': 'EU_UK',
    }
    df['geo_tier'] = df['geo_tier'].replace(geo_map)
    # Final cleanup — map anything not in VALID_GEO to EU_UK if not empty
    valid_geos = {"US","EU_UK","India_seed"}
    def clean_geo(val):
        if not val or val in valid_geos: return val
        return "EU_UK"
    df['geo_tier'] = df['geo_tier'].apply(clean_geo)

# Fix 5 — score_tier: Disqualified → Cold
if 'score_tier' in df.columns:
    df['score_tier'] = df['score_tier'].replace({'Disqualified': 'Cold'})

# Fix 6 — hq_country: full name → ISO code (re-apply in case missed)
country_map = {
    'United States': 'US', 'United Kingdom': 'GB', 'Spain': 'ES',
    'Netherlands': 'NL', 'Montenegro': 'ME', 'India': 'IN',
    'Germany': 'DE', 'France': 'FR', 'Canada': 'CA', 'Australia': 'AU',
    'Singapore': 'SG', 'Israel': 'IL', 'Brazil': 'BR', 'Japan': 'JP',
    'Sweden': 'SE', 'Denmark': 'DK', 'Norway': 'NO', 'Finland': 'FI',
    'Switzerland': 'CH', 'Austria': 'AT', 'Belgium': 'BE', 'Poland': 'PL',
    'Czech Republic': 'CZ', 'Romania': 'RO', 'Hungary': 'HU',
    'Portugal': 'PT', 'Ireland': 'IE', 'New Zealand': 'NZ',
    'South Korea': 'KR', 'China': 'CN', 'Taiwan': 'TW',
    'Hong Kong': 'HK', 'United Arab Emirates': 'AE',
    'South Africa': 'ZA', 'Mexico': 'MX', 'Argentina': 'AR',
    'Chile': 'CL', 'Colombia': 'CO', 'Turkey': 'TR', 'Russia': 'RU',
    'Ukraine': 'UA', 'Pakistan': 'PK', 'Indonesia': 'ID',
    'Malaysia': 'MY', 'Thailand': 'TH', 'Philippines': 'PH',
    'Vietnam': 'VN',
}
if 'hq_country' in df.columns:
    df['hq_country'] = df['hq_country'].replace(country_map)

# Fix 7 — last_funding_date: re-apply date format fix
if 'last_funding_date' in df.columns:
    df['last_funding_date'] = pd.to_datetime(
        df['last_funding_date'], errors='coerce'
    ).dt.strftime('%Y-%m-%d')

# Fix 8 — company_description: truncate to 300 chars
if 'company_description' in df.columns:
    df['company_description'] = df['company_description'].apply(
        lambda x: str(x)[:300] if pd.notna(x) else x
    )

# Fix 9 — LinkedIn URLs
if 'contact_linkedin' in df.columns:
    def fix_contact_linkedin(url):
        if pd.isna(url) or str(url).strip() == '':
            return url
        url = str(url).strip()
        if url.startswith('https://linkedin.com/in/'):
            return url
        if 'linkedin.com/in/' in url:
            slug = url.split('/in/')[-1].rstrip('/')
            return f'https://linkedin.com/in/{slug}'
        return url
    df['contact_linkedin'] = df['contact_linkedin'].apply(fix_contact_linkedin)

if 'company_linkedin' in df.columns:
    def fix_company_linkedin(url):
        if pd.isna(url) or str(url).strip() == '':
            return url
        url = str(url).strip()
        if url.startswith('https://linkedin.com/company/'):
            return url
        if 'linkedin.com/company/' in url:
            slug = url.split('/company/')[-1].rstrip('/')
            return f'https://linkedin.com/company/{slug}'
        return url
    df['company_linkedin'] = df['company_linkedin'].apply(fix_company_linkedin)

df.to_csv('data/scored_leads.csv', index=False)
print("Done. All violations fixed.")
print(f"Total rows: {len(df)}")
