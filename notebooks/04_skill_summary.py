import pandas as pd

from project_config import PROCESSED_FILE, SKILL_SUMMARY_FILE

df = pd.read_csv(PROCESSED_FILE)

skill_terms = [
    "python",
    "sql",
    "r",
    "tableau",
    "power bi",
    "excel",
    "aws",
    "azure",
    "gcp",
    "spark",
    "snowflake",
    "tensorflow",
    "pytorch",
    "machine learning",
    "statistics",
]

text_columns = [
    column
    for column in [
        "skills_text",
        "student_signals.technical_tools_summary",
        "student_signals.requirements_summary",
    ]
    if column in df.columns
]

if not text_columns:
    raise RuntimeError("No skills-related text column was found.")

df["all_skill_text"] = (
    df[text_columns]
    .fillna("")
    .astype(str)
    .agg(" ".join, axis=1)
    .str.lower()
)

skill_summary = pd.DataFrame(
    {
        "skill": skill_terms,
        "postings_mentioning_skill": [
            df["all_skill_text"].str.contains(
                skill,
                regex=False,
                na=False,
            ).sum()
            for skill in skill_terms
        ],
    }
).sort_values("postings_mentioning_skill", ascending=False)

skill_summary.to_csv(SKILL_SUMMARY_FILE, index=False)

print(skill_summary.to_string(index=False))
print("Saved:", SKILL_SUMMARY_FILE)