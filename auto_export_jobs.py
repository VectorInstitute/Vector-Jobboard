import configparser
from utils import get_requests_loop
import os
import pandas as pd
from typing import *

def filter_joblist(jobs: list) -> pd.DataFrame:
    filtered_jobs = pd.DataFrame({
        'token' : [x['token'] for x in jobs],
        'id' : [x['id'] for x in jobs],
        'company' : [x['company'] for x in jobs],
        'title': [x['title'] for x in jobs],
        'remote': [x['remote'] for x in jobs],
        'location': [x['location'] for x in jobs],
        'created_at' : [x['created_at'] for x in jobs],
        'description' : [x['description'] for x in jobs],
        'apply_email' : [x['apply_email'] for x in jobs],
        'apply_url' : [x['apply_url'] for x in jobs],
        'contact_email' : [x['contact_email'] for x in jobs],
        'company_url' : [x['company_url'] for x in jobs],
        'transaction_price' : ["" for x in jobs],
        'revenue_share' : ["" for x in jobs],
        'expiration_date' : [x['expiration_date'] for x in jobs],
        'featured' : [x['featured'] for x in jobs],
        'applicants_count' : [x['applicants_count'] for x in jobs],
        'apply_link_click_count' : [x['apply_link_click_count'] for x in jobs],
        'views' : [x['total_views'] for x in jobs],
        'url' : [x['url'] for x in jobs],
        'reference' : [x['reference'] for x in jobs],
        'status' : [x['status'] for x in jobs],
        'published_at' : [x['published_at'] for x in jobs],
        'source_name' : [x['source_name'] for x in jobs],
        'company_size' : [x['custom_field_answers']['company_size'] if 'company_size' in x['custom_field_answers'].keys() else "" for x in jobs],
        'email_applications_or_application_click_through' : [x['custom_field_answers']['email_applications_or_application_click_through'] if 'email_applications_or_application_click_through' in x['custom_field_answers'].keys() else "" for x in jobs],
        'job_industry' : [", ".join(x['custom_field_answers']['job_industry']) if 'job_industry' in x['custom_field_answers'].keys() else "" for x in jobs],
        'level_of_experience' : [x['custom_field_answers']['level_of_experience'] if 'level_of_experience' in x['custom_field_answers'].keys() else "" for x in jobs],
        'minimum_degree_level' : [x['custom_field_answers']['minimum_degree_level'] if 'minimum_degree_level' in x['custom_field_answers'].keys() else "" for x in jobs],
        'new_posting_or_repost' : [x['custom_field_answers']['new_posting_or_repost'] if 'new_posting_or_repost' in x['custom_field_answers'].keys() else "" for x in jobs],
        'Type of Job Opportunity' : ["" for x in jobs],
    })

    return filtered_jobs

def main() -> None:
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['JOBBOARD']['api_key']
    BASE_URL = 'https://canadaai.jobboard.io/api/v1/jobs/search'
    KEY = 'jobs'
    STATUSES = [
        'draft',
        'published',
        'unpublished',
        'expired'
    ]

    # get all jobs from API
    all_jobs = []
    print("### STARTING ###")
    for status in STATUSES:
        url = BASE_URL + f'?status={status}'
        jobs = get_requests_loop(url, KEY, API_KEY)
        print(f'{status:12} | {len(jobs):7}')
        all_jobs.extend(jobs)
    
    # filter jobs and export to CSV
    print('filtering jobs...')
    filtered_jobs = filter_joblist(all_jobs)
    filtered_jobs.to_csv('jobExport.csv', index=False)

    # push CSV to GitHub
    print('pushing to GitHub...')
    commands = [
        "git fetch --all",
        "git add -f jobExport.csv",
        "git stash push -m export jobExport.csv",
        "git checkout gh-pages",
        "git pull origin gh-pages --rebase",
        "git cherry-pick -n -m1 -Xtheirs stash",
        'git commit -m "Update job export"',
        'git push',
        'git checkout main'
    ]

    for com in commands:
        os.system(com)

    print("### DONE ###")
    return None

if __name__ == "__main__":
    main()