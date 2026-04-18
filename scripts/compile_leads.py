"""
compile_leads.py — P95.AI Lead Engine
Concatenates all normalized lead CSVs from data/raw/ into data/raw_leads.csv.
"""
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUTPUT = Path("data/raw_leads.csv")

NORMALIZED_FILES = [
    "apollo_normalized.csv",
    "seeds_normalized.csv",
    "engineer_normalized.csv",
    "aayush_normalized.csv",
    "linkedin_normalized.csv",
    "healthtech_normalized_gap.csv",
    "ecommerce_normalized_gap.csv",
    "logistics_normalized_gap.csv",
    "cyber_normalized_gap.csv"
]

def main():
    dfs = []
    for fname in NORMALIZED_FILES:
        f = RAW_DIR / fname
        if f.exists():
            df = pd.read_csv(f, dtype=str)
            print(f"Loading {len(df):>4} rows from {fname}")
            dfs.append(df)
    
    if not dfs:
        print("No normalized files found.")
        return

    compiled = pd.concat(dfs, ignore_index=True)
    before = len(compiled)
    
    # Final safety deduplication across all sources
    compiled = compiled.drop_duplicates(subset=["domain", "contact_name"], keep="first")
    dropped = before - len(compiled)
    
    if dropped > 0:
        print(f"Dropped {dropped} cross-file duplicate domains.")
    
    compiled.to_csv(OUTPUT, index=False)
    print(f"\nSuccess! Compiled {len(compiled)} unique leads into {OUTPUT}")

if __name__ == "__main__":
    main()
