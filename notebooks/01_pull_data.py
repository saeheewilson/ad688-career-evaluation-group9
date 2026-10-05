import json
import time

import pandas as pd
import requests

from project_config import (
    API_URL,
    HEADERS,
    RAW_CSV_FILE,
    RAW_JSON_FILE,
)

NAICS_CODE = "5132"
LIMIT = 500
MAX_PAGES = 50
MAX_ATTEMPTS = 3

all_rows = []
offset = 0
pages_completed = 0


if RAW_JSON_FILE.exists():
    with open(RAW_JSON_FILE, "r", encoding="utf-8") as file:
        saved = json.load(file)

    saved_request = saved.get("request", {})

    if (
        saved_request.get("naics") == NAICS_CODE
        and saved_request.get("limit_per_page") == LIMIT
        and "next_offset" in saved
    ):
        all_rows = saved.get("results", [])
        offset = saved["next_offset"]
        pages_completed = saved.get("pages_completed", 0)

        if saved.get("finished", False):
            print("The saved download has already reached the final page.")
        else:
            print(f"Resuming from offset {offset}.")
    else:
        print("No compatible checkpoint found. Starting from offset 0.")

seen_job_ids = {
    row["job_id"]
    for row in all_rows
    if row.get("job_id") is not None
}


def save_progress(finished=False):
    payload = {
        "request": {
            "naics": NAICS_CODE,
            "limit_per_page": LIMIT,
        },
        "next_offset": offset,
        "pages_completed": pages_completed,
        "finished": finished,
        "results": all_rows,
    }

    # Write a temporary file before replacing the saved JSON.
    temporary_file = RAW_JSON_FILE.with_suffix(".json.tmp")

    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)

    temporary_file.replace(RAW_JSON_FILE)

    pd.json_normalize(all_rows).to_csv(RAW_CSV_FILE, index=False)


finished = (
    saved.get("finished", False)
    if RAW_JSON_FILE.exists() and "saved" in locals()
    and saved.get("next_offset") == offset
    else False
)

while pages_completed < MAX_PAGES and not finished:
    print(
        f"Requesting page {pages_completed + 1} "
        f"at offset {offset}..."
    )

    page_payload = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(
                f"{API_URL}/jobs/",
                headers=HEADERS,
                params={
                    "naics": NAICS_CODE,
                    "limit": LIMIT,
                    "offset": offset,
                },
                timeout=180,
            )

            # Retry temporary server failures and rate limits.
            if response.status_code in [429, 500, 502, 503, 504]:
                print(
                    f"API returned {response.status_code}. "
                    f"Attempt {attempt}/{MAX_ATTEMPTS}."
                )
            else:
                response.raise_for_status()
                page_payload = response.json()
                break

        except (requests.Timeout, requests.ConnectionError):
            print(
                f"Connection failed. "
                f"Attempt {attempt}/{MAX_ATTEMPTS}."
            )

        if attempt < MAX_ATTEMPTS:
            time.sleep(10 * attempt)

    if page_payload is None:
        print("Stopping after repeated failures.")
        print(f"Run this script again to resume at offset {offset}.")
        break

    new_rows = page_payload.get("results", [])

    if not new_rows:
        finished = True
        save_progress(finished=True)
        print("No additional rows returned.")
        break

    for row in new_rows:
        job_id = row.get("job_id")

        if job_id is None or job_id not in seen_job_ids:
            all_rows.append(row)

            if job_id is not None:
                seen_job_ids.add(job_id)

    # Advance by the number returned, independently of duplicates.
    offset += len(new_rows)
    pages_completed += 1

    finished = (
        page_payload.get("meta", {}).get("has_more") is False
    )

    save_progress(finished=finished)

    print(
        f"Received {len(new_rows)} rows. "
        f"Saved {len(all_rows)} unique rows."
    )

    if finished:
        print("Reached the final API page.")
        break

    time.sleep(0.3)

print("Total saved rows:", len(all_rows))
print("JSON:", RAW_JSON_FILE)
print("CSV:", RAW_CSV_FILE)