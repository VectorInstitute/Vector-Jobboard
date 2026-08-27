import pandas as pd
import json
import requests
import sys
import time
import random

MIN_DELAY = 10
MAX_DELAY = 15
MAX_RETRIES = 8
INITIAL_BACKOFF = 15
MAX_BACKOFF = 300

BATCH_SIZE = 25
BATCH_DELAY_MIN = 60
BATCH_DELAY_MAX = 90

def request_with_retry(method, url, headers, **kwargs):
    backoff = INITIAL_BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.request(method, url, headers=headers, timeout=60, **kwargs)
        except requests.RequestException as error:
            print("Network error:", error)
            if attempt >= MAX_RETRIES:
                return None
            time.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)
            continue

        if 200 <= response.status_code < 300:
            return response

        if response.status_code == 429:
            print("429 rate limited, attempt", attempt)
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    wait_time = float(retry_after)
                except ValueError:
                    wait_time = backoff
            else:
                wait_time = backoff
            wait_time += random.uniform(0, 5)
            print("Waiting", round(wait_time, 1), "seconds before retry...")
            time.sleep(wait_time)
            backoff = min(backoff * 2, MAX_BACKOFF)
            continue

        if response.status_code in (500, 502, 503, 504):
            print("Temporary server error:", response.status_code)
            if attempt >= MAX_RETRIES:
                return response
            time.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)
            continue

        # 401/403/other errors - don't keep retrying
        return response

    return None

def main():
    print(sys.argv)
    API_KEY = sys.argv[1]
    JOBBOARD_API_KEY = sys.argv[2]
    owner = 'VectorInstitute'
    repo = 'Vector-Jobboard'
    path = 'OldProfiles_ProfilesExport.csv'
    branchName = 'gh-pages'
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branchName}"
    response = requests.get(url, headers = { "Authorization": "Bearer " + API_KEY})
    data = response.json()
    csvUrl = data['download_url']
    df = pd.read_csv(csvUrl)

    # The CSV itself already records each profile's current hidden status,
    # so there's no need to GET and check all of them - only the ones
    # marked False actually need work. This is what keeps the run well
    # under GitHub Actions' 6-hour job limit.
    id_col = df.columns[0]
    if 'hidden' in df.columns:
        to_process = df[df['hidden'] == False]
        print(f"Total profiles in CSV: {len(df)}")
        print(f"Already hidden (skipped, no API call): {len(df) - len(to_process)}")
        print(f"Needing action: {len(to_process)}")
    else:
        to_process = df
        print("No 'hidden' column found in CSV - falling back to checking every profile.")

    x = to_process[id_col].dropna().values
    headers = {
        "Accept": "application/json",
        "JobBoardioURL": "https://talenthub.vectorinstitute.ai/",
        "X-Api-Key" : JOBBOARD_API_KEY
    }
    hidden_count = 0
    already_hidden_count = 0
    failed_count = 0
    total = len(x)
    num_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

    est_seconds = total * ((MIN_DELAY + MAX_DELAY) / 2) + num_batches * ((BATCH_DELAY_MIN + BATCH_DELAY_MAX) / 2)
    print(f"Estimated minimum runtime: ~{round(est_seconds / 60, 1)} minutes for {total} profiles across {num_batches} batches.")

    for batch_num in range(num_batches):
        batch_start = batch_num * BATCH_SIZE
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch_ids = x[batch_start:batch_end]

        print()
        print("=" * 65)
        print(f"BATCH {batch_num + 1}/{num_batches}  (profiles {batch_start + 1}-{batch_end} of {total})")
        print("=" * 65)

        for i, profile_id in enumerate(batch_ids):
            ID = batch_start + i
            url = "https://canadaai.jobboard.io/api/v1/profiles/" + str(profile_id)
            print(f"[{ID + 1}/{total}] Profile {profile_id}")

            response = request_with_retry("GET", url, headers)
            if response is None or response.status_code != 200:
                print("  GET failed")
                failed_count += 1
            else:
                data = json.loads(response.text)
                profile = data.get('profile')
                if profile is None:
                    print("  No profile in response")
                    failed_count += 1
                elif profile.get('hidden') is True or str(profile.get('hidden')).lower() == 'true':
                    print("  Already hidden")
                    already_hidden_count += 1
                else:
                    payload = {"hidden": True}
                    patch_response = request_with_retry("PATCH", url, headers, json=payload)
                    if patch_response is not None and 200 <= patch_response.status_code < 300:
                        print("  Hidden")
                        hidden_count += 1
                    else:
                        print("  PATCH failed")
                        failed_count += 1

            if ID < total - 1:
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                time.sleep(delay)

        if batch_num < num_batches - 1:
            batch_delay = random.uniform(BATCH_DELAY_MIN, BATCH_DELAY_MAX)
            print()
            print(f"Batch {batch_num + 1} complete. Waiting {round(batch_delay, 1)} seconds before next batch...")
            time.sleep(batch_delay)

    print()
    print("=" * 65)
    print("COMPLETE")
    print("=" * 65)
    print("Hidden:", hidden_count)
    print("Already hidden (confirmed via API):", already_hidden_count)
    print("Failed:", failed_count)
if __name__ == "__main__":
    main()
