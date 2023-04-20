import sys

from auto_export_employers import filter_employer_list
from auto_export_jobs import filter_joblist
from auto_export_profiles import filter_profile_list
from utils import get_requests_loop


def main():

    API_KEY = sys.argv[1]

    # employer export
    BASE_URL_EMPLOYER = 'https://canadaai.jobboard.io/api/v1/employers'
    KEY_EMPLOYER = 'employers'
    all_employers = []
    print("### STARTING EMPLOYERS ###")
    url = BASE_URL_EMPLOYER
    employers = get_requests_loop(url, KEY_EMPLOYER, API_KEY)
    print(f'{"employers":12} | {len(employers):7}')
    all_employers.extend(employers)
    # filter employers and export to CSV
    print('filtering employers...')
    filtered_employers = filter_employer_list(all_employers)
    filtered_employers.to_csv('employerExport.csv', index=False)


    # jobs export
    BASE_URL_JOBS = 'https://canadaai.jobboard.io/api/v1/jobs/search'
    KEY_JOBS = 'jobs'
    STATUSES = [
        'draft',
        'published',
        'unpublished',
        'expired'
    ]
    # get all jobs from API
    all_jobs = []
    print("### STARTING JOBS ###")
    for status in STATUSES:
        url = BASE_URL_JOBS + f'?status={status}'
        jobs = get_requests_loop(url, KEY_JOBS, API_KEY)
        print(f'{status:12} | {len(jobs):7}')
        all_jobs.extend(jobs)
    # filter jobs and export to CSV
    print('filtering jobs...')
    filtered_jobs = filter_joblist(all_jobs)
    filtered_jobs.to_csv('jobExport.csv', index=False)


    # profiles export
    BASE_URL_PROFILES = 'https://canadaai.jobboard.io/api/v1/profiles'
    KEY_PROFILES = 'profiles'
    # get all profiles from API
    all_profiles = []
    print("### STARTING PROFILES ###")
    url = BASE_URL_PROFILES
    profiles = get_requests_loop(url, KEY_PROFILES, API_KEY)
    print(f'{"profiles":12} | {len(profiles):7}')
    all_profiles.extend(profiles)
    # filter profiles and export to CSV
    print('filtering profiles...')
    filtered_profiles = filter_profile_list(all_profiles)
    filtered_profiles.to_csv('profileExport.csv', index=False)

    print("### DONE ###")

    return None


if __name__ == "__main__":
    main()