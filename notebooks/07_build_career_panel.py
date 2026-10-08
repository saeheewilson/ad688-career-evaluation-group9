"""
Module 5 prep: build career_market_panel.csv from the enhanced Module 3 dataset.

Adds:
  - role_segment: groups the broad SOC "Data Scientists" titles into job families
  - education flags, remote flag, Oracle flag
  - one 0/1 column per team-comparison skill (skill_sql, skill_python, ...)
Also writes a data dictionary for the panel.
"""

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "module3"

SOURCE_FILE = DATA_DIR / "data_scientist_software_publishers_clean.csv"
PANEL_FILE = DATA_DIR / "career_market_panel.csv"
DICTIONARY_FILE = DATA_DIR / "career_market_panel_dictionary.csv"

df = pd.read_csv(SOURCE_FILE, low_memory=False)

# ---------------------------------------------------------------
# 1. Role segments
# ---------------------------------------------------------------
SEGMENT_RULES = [
    ("Data Scientist / ML", r"data scien|machine learning|\bml\b|applied scien|\bai engineer"),
    ("AI Data Trainer", r"\btrainer\b"),
    ("Data / BI Analyst", r"data analy|business intelligence|\bbi\b|analytics|reporting analyst|data modeler|insights"),
    ("Sales / Pre-Sales", r"sales|account exec|business development"),
    ("Consultant / Implementation", r"consult|implementation|functional|practice"),
    ("Architect / Engineer", r"architect|engineer|developer"),
]


def assign_segment(title):
    title = str(title).lower()
    for segment, pattern in SEGMENT_RULES:
        if re.search(pattern, title):
            return segment
    return "Other Business / Analyst"


df["role_segment"] = df["TITLE_CLEAN"].apply(assign_segment)

# ---------------------------------------------------------------
# 2. Simple flags
# ---------------------------------------------------------------
education = df["EDUCATION_LEVELS_NAME"].fillna("")

df["edu_bachelors"] = education.str.contains("Bachelor", regex=False).astype(int)
df["edu_masters"] = education.str.contains("Master", regex=False).astype(int)
df["edu_phd"] = education.str.contains("Ph.D", regex=False).astype(int)
df["edu_not_listed"] = education.str.contains("No Education Listed", regex=False).astype(int)

df["remote_clean"] = df["REMOTE_TYPE_NAME"].replace("[None]", "Not specified")
df["is_remote"] = (df["remote_clean"] == "Remote").astype(int)
df["is_full_time"] = df["EMPLOYMENT_TYPE_NAME"].str.startswith("Full").astype(int)
df["is_oracle"] = (df["COMPANY_NAME"] == "Oracle").astype(int)
df["posted_month"] = pd.to_datetime(df["POSTED"], errors="coerce").dt.to_period("M").astype(str)

# ---------------------------------------------------------------
# 3. Skill flags (same skill names used on the Skill Gap page)
# ---------------------------------------------------------------
SKILL_NAMES = {
    "skill_sql": "SQL (Programming Language)",
    "skill_python": "Python (Programming Language)",
    "skill_tableau": "Tableau (Business Intelligence Software)",
    "skill_power_bi": "Power BI",
    "skill_statistics": "Statistics",
    "skill_machine_learning": "Machine Learning",
    "skill_excel": "Microsoft Excel",
    "skill_azure": "Microsoft Azure",
    "skill_aws": "Amazon Web Services",
    "skill_gcp": "Google Cloud Platform (GCP)",
    "skill_spark": "Apache Spark",
}

skill_lists = df["SKILLS_NAME"].fillna("[]").apply(json.loads)

for column, skill in SKILL_NAMES.items():
    df[column] = skill_lists.apply(lambda skills: int(skill in skills))

df["skill_count"] = skill_lists.apply(len)

# ---------------------------------------------------------------
# 4. Save the panel and a data dictionary
# ---------------------------------------------------------------
keep_columns = [
    "ID", "POSTED", "posted_month", "TITLE_RAW", "TITLE_CLEAN", "role_segment",
    "COMPANY_NAME", "is_oracle", "CITY_NAME", "STATE_NAME",
    "remote_clean", "is_remote", "EMPLOYMENT_TYPE_NAME", "is_full_time",
    "MIN_YEARS_EXPERIENCE", "MAX_YEARS_EXPERIENCE",
    "edu_bachelors", "edu_masters", "edu_phd", "edu_not_listed",
    "SALARY_FROM", "SALARY_TO", "SALARY_MIDPOINT",
    "skill_count", *SKILL_NAMES.keys(),
]

panel = df[keep_columns]
panel.to_csv(PANEL_FILE, index=False)

descriptions = {
    "ID": "Unique posting identifier.",
    "POSTED": "Posting date.",
    "posted_month": "Posting month (YYYY-MM).",
    "TITLE_RAW": "Original job title.",
    "TITLE_CLEAN": "Lower-cased, cleaned job title.",
    "role_segment": "Job family assigned from title keywords (see notebooks/07_build_career_panel.py).",
    "COMPANY_NAME": "Employer name.",
    "is_oracle": "1 if the employer is Oracle (largest employer in the sample).",
    "CITY_NAME": "City of the posting.",
    "STATE_NAME": "State of the posting.",
    "remote_clean": "Remote, Hybrid Remote, Not Remote, or Not specified.",
    "is_remote": "1 if classified as fully Remote.",
    "EMPLOYMENT_TYPE_NAME": "Full-time or part-time classification.",
    "is_full_time": "1 if full-time.",
    "MIN_YEARS_EXPERIENCE": "Minimum years of experience required (blank if not stated).",
    "MAX_YEARS_EXPERIENCE": "Maximum years of experience (blank if not stated).",
    "edu_bachelors": "1 if a bachelor's degree is listed.",
    "edu_masters": "1 if a master's degree is listed.",
    "edu_phd": "1 if a Ph.D. or professional degree is listed.",
    "edu_not_listed": "1 if no education requirement is listed.",
    "SALARY_FROM": "Lower bound of posted annual salary.",
    "SALARY_TO": "Upper bound of posted annual salary.",
    "SALARY_MIDPOINT": "Average of SALARY_FROM and SALARY_TO.",
    "skill_count": "Number of standardized skills listed in the posting.",
}
for column, skill in SKILL_NAMES.items():
    descriptions[column] = f"1 if the posting lists '{skill}'."

dictionary = pd.DataFrame(
    {"variable": list(descriptions.keys()), "description": list(descriptions.values())}
)
dictionary.to_csv(DICTIONARY_FILE, index=False)

print("Rows:", len(panel))
print("\nPostings by role segment:")
print(panel["role_segment"].value_counts().to_string())
print("\nSaved:", PANEL_FILE)
print("Saved:", DICTIONARY_FILE)