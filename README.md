# Career Evaluation: Data Scientist–Classified Roles in Software Publishers

AD688 Fall 2026, Group 9

This repository contains a Quarto website and report that evaluate job postings classified under the Data Scientists occupation in the Software Publishers industry (NAICS 5132), with the goal of helping students understand which roles are realistic starting points and which skills to prioritize.

Live site: https://saeheewilson.github.io/ad688-career-evaluation-group9/

## Team Contributions

Sae Hee Wilson set up the team repository, and all three team members chose the industry, NAICS code, and target career pathway together. Dylan Thomson completed the rest of Module 1 and all of Module 3, including the project framing, literature review, enhanced dataset, exploratory analysis, skill-gap analysis, and modeling plan. Richard Wu completed Module 2, including the API data pipeline, cleaning, and data preparation. Sae Hee Wilson completed the Module 4 checkpoint and Module 5, including the role segmentation, career market panel and data dictionary, job volume by segment, scorecard, salary models, recommendations, and the final report.

## Site Pages

| Page | File |
|---|---|
| Home | `index.qmd` |
| Project Overview | `introduction.qmd` |
| Data Preparation | `data_cleaning.qmd` |
| Exploratory Analysis | `eda.qmd` |
| Skill Gap Analysis | `skill_gap_analysis.qmd` |
| Career Evaluation | `career_evaluation.qmd` |
| Predictive Modeling | `ml_methods.qmd` |
| Career Strategy | `career_plan.qmd` |
| Final Report (Word) | `final_report.qmd` |

## Data

- `data/module3/data_scientist_software_publishers_clean.csv` is the cleaned 1,016-posting dataset used for the analysis.
- `data/module3/career_market_panel.csv` adds role segments and skill flags, and is created by `notebooks/07_build_career_panel.py`.
- `data/module3/career_market_panel_dictionary.csv` describes each variable in the panel.
- `notebooks/01_pull_data.py` through `06_market_summary.py` are the original MET Career Compass API pipeline from Module 2.
- `notebooks/explore_titles.ipynb` shows the job-title review behind the role segments.

Raw data files are not committed.

## Running the Project

1. Create and activate a virtual environment, then install packages with `pip install -r requirements.txt`.
2. To use the API scripts, copy `.env.example` to `.env` and add your MET Employability API key. Do not commit `.env`.
3. Run `python notebooks/07_build_career_panel.py` to rebuild the career panel.
4. Run `quarto preview` to view the site, or `quarto render final_report.qmd --to docx` to build the report.