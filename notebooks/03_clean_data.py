import re

import pandas as pd

from project_config import PROCESSED_FILE, ROLE_MATCHES_FILE

clean_df = pd.read_csv(ROLE_MATCHES_FILE)

staffing_terms = [
    "staffing",
    "recruit",
    "recruiting",
    "talent",
    "employment",
    "personaldienst",
    "personalservice",
    "constaff",
    "akkodis",
    "orizon",
    "cure-x",
]

staffing_pattern = "|".join(
    re.escape(term)
    for term in staffing_terms
)

clean_df["company_clean"] = (
    clean_df["company_name"]
    .fillna("")
    .str.lower()
    .str.strip()
)

clean_df["company_name_staffing_flag"] = (
    clean_df["company_clean"]
    .str.contains(staffing_pattern, regex=True, na=False)
)

if "is_staffing_agency" in clean_df.columns:
    clean_df["api_staffing_flag"] = (
        clean_df["is_staffing_agency"]
        .fillna(False)
        .astype(str)
        .str.lower()
        .isin(["true", "1", "yes"])
    )
else:
    clean_df["api_staffing_flag"] = False

clean_df["staffing_flag"] = (
    clean_df["company_name_staffing_flag"]
    | clean_df["api_staffing_flag"]
)

staffing_rows_removed = clean_df["staffing_flag"].sum()

clean_df = clean_df[~clean_df["staffing_flag"]].copy()
clean_df = clean_df.drop_duplicates(subset="job_id")

for column in ["posted_at", "expires_at"]:
    if column in clean_df.columns:
        clean_df[column] = pd.to_datetime(
            clean_df[column],
            errors="coerce",
            utc=True,
        )

for column in ["annual_salary_min", "annual_salary_max"]:
    if column in clean_df.columns:
        clean_df[column] = pd.to_numeric(
            clean_df[column],
            errors="coerce",
        )
        clean_df.loc[clean_df[column] <= 0, column] = pd.NA

if {
    "annual_salary_min",
    "annual_salary_max",
}.issubset(clean_df.columns):
    clean_df["annual_salary_midpoint"] = (
        clean_df["annual_salary_min"]
        + clean_df["annual_salary_max"]
    ) / 2

if "remote_status" in clean_df.columns:
    clean_df["remote_status_clean"] = (
        clean_df["remote_status"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.title()
    )

helper_columns = [
    "title_clean",
    "role_match",
    "company_clean",
    "company_name_staffing_flag",
    "api_staffing_flag",
]

clean_df = clean_df.drop(
    columns=[
        column
        for column in helper_columns
        if column in clean_df.columns
    ]
)

clean_df.to_csv(PROCESSED_FILE, index=False)

print("Staffing-agency rows removed:", staffing_rows_removed)
print("Final cleaned rows:", len(clean_df))
print("Saved:", PROCESSED_FILE)