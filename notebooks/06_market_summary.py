import pandas as pd

from project_config import ROOT, PROCESSED_FILE

OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(PROCESSED_FILE)

if df.empty:
    raise RuntimeError("The cleaned dataset is empty.")

print("Cleaned postings:", len(df))
print("Unique employers:", df["company_name"].nunique())

# Show missing-data coverage for every column.
coverage = pd.DataFrame({
    "variable": df.columns,
    "non_missing_rows": df.notna().sum().values,
    "missing_rows": df.isna().sum().values,
    "missing_percent": (df.isna().mean() * 100).round(1).values,
})

coverage.to_csv(
    OUTPUT_DIR / "data_coverage.csv",
    index=False,
)

# Create posting-count tables.
summary_columns = [
    "title",
    "role_group",
    "company_name",
    "state_code",
    "city",
    "remote_status_clean",
]

for column in summary_columns:
    if column not in df.columns:
        continue

    values = (
        df[column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
    )

    summary = (
        values.value_counts()
        .rename_axis(column)
        .reset_index(name="postings")
    )

    summary["percent_of_postings"] = (
        summary["postings"] / len(df) * 100
    ).round(1)

    output_file = OUTPUT_DIR / f"counts_by_{column}.csv"
    summary.to_csv(output_file, index=False)

    print(f"\n=== {column.upper()} ===")
    print(summary.head(15).to_string(index=False))

# Report salary coverage without combining unverified currencies.
salary_columns = [
    column
    for column in [
        "annual_salary_min",
        "annual_salary_max",
        "annual_salary_midpoint",
    ]
    if column in df.columns
]

if salary_columns:
    salary_data = df[salary_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    salary_coverage = pd.DataFrame({
        "variable": salary_columns,
        "postings_with_value": salary_data.notna().sum().values,
    })

    salary_coverage.to_csv(
        OUTPUT_DIR / "salary_coverage.csv",
        index=False,
    )

    print("\n=== SALARY COVERAGE ===")
    print(salary_coverage.to_string(index=False))

print("\nSaved summary tables to:", OUTPUT_DIR)