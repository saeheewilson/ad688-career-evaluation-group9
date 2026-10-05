import pandas as pd

from project_config import DICTIONARY_FILE

data_dictionary = pd.DataFrame(
    [
        ["job_id", "Unique job-posting identifier from the MET API."],
        ["title", "Original job title from the posting."],
        ["company_name", "Employer name listed in the posting."],
        ["naics_code", "Industry code supplied by the API."],
        ["naics_name", "Industry name supplied by the API."],
        ["posted_at", "Date when the job posting was published."],
        ["remote_status_clean", "Remote, hybrid, onsite, or unknown work arrangement."],
        ["annual_salary_min", "Lowest reported annual salary."],
        ["annual_salary_max", "Highest reported annual salary."],
        ["annual_salary_midpoint", "Average of annual minimum and maximum salary."],
        ["skills_text", "Skills text supplied by the API, when available."],
    ],
    columns=["variable", "description"],
)

data_dictionary.to_csv(DICTIONARY_FILE, index=False)

print(data_dictionary.to_string(index=False))
print("Saved:", DICTIONARY_FILE)