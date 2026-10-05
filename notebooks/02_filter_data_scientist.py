import json

import pandas as pd

from project_config import RAW_JSON_FILE, ROLE_MATCHES_FILE

# Load the saved raw API data.
if not RAW_JSON_FILE.exists():
    raise RuntimeError("Run 01_pull_data.py first.")

with open(RAW_JSON_FILE, "r", encoding="utf-8") as file:
    raw_payload = json.load(file)

raw_df = pd.json_normalize(raw_payload.get("results", []))

if raw_df.empty:
    raise RuntimeError("The saved raw dataset contains no postings.")

required_columns = {"job_id", "title", "company_name"}
missing_columns = required_columns - set(raw_df.columns)

if missing_columns:
    raise RuntimeError(
        f"Missing required columns: {sorted(missing_columns)}"
    )

raw_df = raw_df.drop_duplicates(subset="job_id").copy()

# Normalize job titles.
raw_df["title_clean"] = (
    raw_df["title"]
    .fillna("")
    .astype(str)
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# Include Data Scientist and related AI/ML careers.
role_terms = [
    r"\bdata[\s-]+scientists?\b",
    r"\bmachine learning[\s-]+scientists?\b",
    r"\bapplied[\s-]+scientists?\b",
    r"\bresearch[\s-]+scientists?\b",
    r"\bmachine learning[\s-]+engineers?\b",
    r"\bml[\s-]+engineers?\b",
    r"\bai[\s-]+engineers?\b",
]

role_pattern = "|".join(role_terms)

raw_df["role_match"] = raw_df["title_clean"].str.contains(
    role_pattern,
    regex=True,
    na=False,
)

role_df = raw_df[raw_df["role_match"]].copy()

# Label direct Data Scientist matches separately from related roles.
direct_match = role_df["title_clean"].str.contains(
    r"\bdata[\s-]+scientists?\b",
    regex=True,
    na=False,
)

role_df["role_group"] = "Related AI/ML role"
role_df.loc[direct_match, "role_group"] = "Data Scientist"

role_df["industry_verification"] = "Pending employer review"

# Save matches for 03_clean_data.py.
role_df.to_csv(ROLE_MATCHES_FILE, index=False)

# Identify additional candidates using SOC or Data Science titles.
soc_names = raw_df.get(
    "soc_name",
    pd.Series("", index=raw_df.index),
)

soc_match = (
    soc_names
    .fillna("")
    .astype(str)
    .str.lower()
    .str.contains(
        r"\bdata[\s-]+scientists?\b",
        regex=True,
        na=False,
    )
)

data_science_title = raw_df["title_clean"].str.contains(
    r"\bdata science\b",
    regex=True,
    na=False,
)

review_df = raw_df[
    ~raw_df["role_match"]
    & (soc_match | data_science_title)
].copy()

review_df["review_status"] = "Pending role and employer review"

review_file = (
    ROLE_MATCHES_FILE.parent / "related_roles_to_review.csv"
)

review_df.to_csv(review_file, index=False)

# Print results.
display_columns = [
    column
    for column in [
        "job_id",
        "title",
        "company_name",
        "soc_name",
        "naics_code",
        "naics_name",
    ]
    if column in raw_df.columns
]

print("Unique raw postings:", len(raw_df))
print("Data Scientist and related-role matches:", len(role_df))
print("Explicit Data Scientist titles:", int(direct_match.sum()))
print("Related AI/ML titles:", int((~direct_match).sum()))

print("\n=== MATCHED ROLES ===")
print(
    role_df[display_columns + ["role_group"]]
    .to_string(index=False)
)

print("\n=== ADDITIONAL CANDIDATES FOR REVIEW ===")
print("Additional candidates:", len(review_df))
print(review_df[display_columns].to_string(index=False))

print("\nSaved matches:", ROLE_MATCHES_FILE)
print("Saved review candidates:", review_file)