import pandas as pd
import requests
import sys
import time
import random


# ============================================================
# SETTINGS
# ============================================================

BASE_URL = "https://canadaai.jobboard.io/api/v1/profiles/"
JOBBOARD_URL = "https://talenthub.vectorinstitute.ai/"

# ------------------------------------------------------------
# TEST MODE
# ------------------------------------------------------------
# True  = only process the first TEST_PROFILE_LIMIT profiles
# False = process the entire CSV
#
# KEEP TRUE FOR THE FIRST TEST.
# ------------------------------------------------------------

TEST_MODE = True
TEST_PROFILE_LIMIT = 3

# ------------------------------------------------------------
# NORMAL DELAY
# ------------------------------------------------------------
# Delay between profiles.
#
# We are deliberately conservative because the API has
# already demonstrated 429 rate limiting.
# ------------------------------------------------------------

MIN_DELAY = 10
MAX_DELAY = 15

# ------------------------------------------------------------
# RETRY SETTINGS
# ------------------------------------------------------------

MAX_RETRIES = 8

INITIAL_BACKOFF = 15

MAX_BACKOFF = 300


# ============================================================
# PRINT 429 INFORMATION
# ============================================================

def print_rate_limit_info(response):

    print()
    print("  ---------------- RATE LIMIT ----------------")

    print(
        f"  HTTP status: {response.status_code}"
    )

    retry_after = response.headers.get(
        "Retry-After"
    )

    print(
        f"  Retry-After: "
        f"{retry_after if retry_after else 'not provided'}"
    )

    interesting_headers = [
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
        "RateLimit-Limit",
        "RateLimit-Remaining",
        "RateLimit-Reset",
    ]

    for header in interesting_headers:

        value = response.headers.get(header)

        if value is not None:

            print(
                f"  {header}: {value}"
            )

    body = response.text.strip()

    if body:

        print()
        print("  Response body:")

        print(
            body[:1000]
        )

    print(
        "  --------------------------------------------"
    )


# ============================================================
# API REQUEST WITH RETRIES
# ============================================================

def request_with_retry(
    session,
    method,
    url,
    headers,
    **kwargs
):

    backoff = INITIAL_BACKOFF

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        print(
            f"  {method} attempt "
            f"{attempt}/{MAX_RETRIES}"
        )

        try:

            response = session.request(
                method,
                url,
                headers=headers,
                timeout=60,
                **kwargs
            )

        except requests.RequestException as error:

            print()
            print(
                f"  Network error: {error}"
            )

            if attempt >= MAX_RETRIES:

                print(
                    "  Maximum retries reached."
                )

                return None

            print(
                f"  Waiting {backoff} seconds..."
            )

            time.sleep(backoff)

            backoff = min(
                backoff * 2,
                MAX_BACKOFF
            )

            continue

        # ====================================================
        # SUCCESS
        # ====================================================

        if 200 <= response.status_code < 300:

            print(
                f"  HTTP {response.status_code}"
            )

            return response

        # ====================================================
        # RATE LIMITED
        # ====================================================

        if response.status_code == 429:

            print()
            print(
                "  !!! 429 TOO MANY REQUESTS !!!"
            )

            print_rate_limit_info(
                response
            )

            retry_after = response.headers.get(
                "Retry-After"
            )

            if retry_after:

                try:

                    wait_time = float(
                        retry_after
                    )

                except ValueError:

                    wait_time = backoff

            else:

                wait_time = backoff

            # Add small randomization
            wait_time += random.uniform(
                0,
                5
            )

            print()
            print(
                f"  Waiting {wait_time:.1f} "
                f"seconds before retry..."
            )

            time.sleep(
                wait_time
            )

            backoff = min(
                backoff * 2,
                MAX_BACKOFF
            )

            continue

        # ====================================================
        # TEMPORARY SERVER ERROR
        # ====================================================

        if response.status_code in (
            500,
            502,
            503,
            504
        ):

            print()
            print(
                f"  Temporary server error: "
                f"{response.status_code}"
            )

            if attempt >= MAX_RETRIES:

                return response

            print(
                f"  Waiting {backoff} seconds..."
            )

            time.sleep(
                backoff
            )

            backoff = min(
                backoff * 2,
                MAX_BACKOFF
            )

            continue

        # ====================================================
        # AUTHENTICATION
        # ====================================================

        if response.status_code in (
            401,
            403
        ):

            print()
            print(
                f"  AUTHENTICATION/PERMISSION "
                f"ERROR: {response.status_code}"
            )

            print(
                f"  Response: "
                f"{response.text[:1000]}"
            )

            # Don't repeatedly retry credentials that
            # are invalid or unauthorized.
            return response

        # ====================================================
        # OTHER ERROR
        # ====================================================

        print()
        print(
            f"  API error: "
            f"{response.status_code}"
        )

        print(
            f"  Response: "
            f"{response.text[:1000]}"
        )

        return response

    return None


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 65)
    print("VECTOR TALENT HUB - HIDE OLD PROFILES")
    print("=" * 65)
    print()

    # ========================================================
    # CHECK ARGUMENTS
    # ========================================================

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print()

        print(
            "python hide_profiles.py "
            "<GITHUB_TOKEN> "
            "<JOBBOARD_TOKEN>"
        )

        sys.exit(1)

    GITHUB_TOKEN = sys.argv[1]

    JOBBOARD_TOKEN = sys.argv[2]

    # ========================================================
    # GITHUB CSV
    # ========================================================

    owner = "VectorInstitute"

    repo = "Vector-Jobboard"

    path = "OldProfiles_ProfilesExport.csv"

    branch_name = "gh-pages"

    github_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/contents/"
        f"{path}?ref={branch_name}"
    )

    github_headers = {
        "Authorization":
            "Bearer " + GITHUB_TOKEN,

        "Accept":
            "application/vnd.github+json"
    }

    print(
        "Downloading profile list..."
    )

    try:

        github_response = requests.get(
            github_url,
            headers=github_headers,
            timeout=60
        )

        print(
            f"GitHub response: "
            f"{github_response.status_code}"
        )

        github_response.raise_for_status()

        github_data = (
            github_response.json()
        )

        csv_url = (
            github_data["download_url"]
        )

        df = pd.read_csv(
            csv_url
        )

    except Exception as error:

        print()
        print(
            "ERROR downloading CSV:"
        )

        print(error)

        sys.exit(1)

    # ========================================================
    # PROFILE IDS
    # ========================================================

    profile_ids = (
        df.iloc[:, 0]
        .dropna()
        .astype(str)
        .tolist()
    )

    print()
    print(
        f"Profiles found: "
        f"{len(profile_ids)}"
    )

    # ========================================================
    # TEST MODE
    # ========================================================

    if TEST_MODE:

        profile_ids = (
            profile_ids[
                :TEST_PROFILE_LIMIT
            ]
        )

        print()
        print(
            "!!! TEST MODE ENABLED !!!"
        )

        print(
            f"Only the first "
            f"{len(profile_ids)} "
            f"profiles will be processed."
        )

    else:

        print()
        print(
            "FULL MODE ENABLED"
        )

        print(
            "The entire CSV will be processed."
        )

    print()

    # ========================================================
    # JOBBOARD HEADERS
    # ========================================================

    headers = {

        "Accept":
            "application/json",

        "Content-Type":
            "application/json",

        "JobBoardioURL":
            JOBBOARD_URL,

        "X-Api-Key":
            JOBBOARD_TOKEN
    }

    # ========================================================
    # SESSION
    # ========================================================

    session = requests.Session()

    # ========================================================
    # COUNTERS
    # ========================================================

    hidden_count = 0

    already_hidden_count = 0

    failed_count = 0

    total = len(profile_ids)

    # ========================================================
    # PROCESS PROFILES
    # ========================================================

    for index, profile_id in enumerate(
        profile_ids,
        start=1
    ):

        print()
        print("=" * 65)

        print(
            f"[{index}/{total}] "
            f"Profile {profile_id}"
        )

        print("=" * 65)

        profile_url = (
            BASE_URL + profile_id
        )

        # ====================================================
        # GET PROFILE
        # ====================================================

        print(
            "  Checking profile..."
        )

        response = request_with_retry(
            session,
            "GET",
            profile_url,
            headers
        )

        if response is None:

            print(
                "  FAILED: no response."
            )

            failed_count += 1

            continue

        # ====================================================
        # HANDLE GET FAILURE
        # ====================================================

        if response.status_code != 200:

            print(
                f"  GET failed: "
                f"HTTP {response.status_code}"
            )

            failed_count += 1

            continue

        # ====================================================
        # PARSE JSON
        # ====================================================

        try:

            data = response.json()

        except ValueError:

            print()
            print(
                "  ERROR: API returned "
                "non-JSON response."
            )

            print(
                response.text[:1000]
            )

            failed_count += 1

            continue

        # ====================================================
        # GET PROFILE OBJECT
        # ====================================================

        profile = data.get(
            "profile",
            {}
        )

        hidden = profile.get(
            "hidden"
        )

        print(
            f"  Current hidden status: "
            f"{hidden}"
        )

        # ====================================================
        # ALREADY HIDDEN
        # ====================================================

        if (
            hidden is True
            or str(hidden).lower() == "true"
        ):

            print(
                "  Already hidden."
            )

            already_hidden_count += 1

        else:

            # =================================================
            # PATCH PROFILE
            # =================================================

            print(
                "  Sending PATCH..."
            )

            payload = {
                "hidden": True
            }

            patch_response = (
                request_with_retry(
                    session,
                    "PATCH",
                    profile_url,
                    headers,
                    json=payload
                )
            )

            if patch_response is None:

                print(
                    "  PATCH failed: "
                    "no response."
                )

                failed_count += 1

            elif (
                200
                <= patch_response.status_code
                < 300
            ):

                print()
                print(
                    "  SUCCESS: profile hidden."
                )

                hidden_count += 1

            else:

                print()
                print(
                    f"  PATCH failed: "
                    f"HTTP "
                    f"{patch_response.status_code}"
                )

                print(
                    patch_response.text[:1000]
                )

                failed_count += 1

        # ====================================================
        # DELAY BEFORE NEXT PROFILE
        # ====================================================

        if index < total:

            delay = random.uniform(
                MIN_DELAY,
                MAX_DELAY
            )

            print()
            print(
                f"  Waiting "
                f"{delay:.1f} seconds "
                f"before next profile..."
            )

            time.sleep(
                delay
            )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 65)
    print("COMPLETE")
    print("=" * 65)

    print(
        f"Total processed:   {total}"
    )

    print(
        f"Successfully hidden: "
        f"{hidden_count}"
    )

    print(
        f"Already hidden:    "
        f"{already_hidden_count}"
    )

    print(
        f"Failed:            "
        f"{failed_count}"
    )

    print("=" * 65)
    print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
