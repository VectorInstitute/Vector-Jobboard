import configparser
from utils import get_requests_loop
import os
import pandas as pd
from typing import *

def filter_employer_list(employers: list) -> pd.DataFrame:
    filtered_employers = pd.DataFrame({
        'id' : [x['id'] for x in employers],
        'email' : [x['email'] for x in employers],
        'name': [x['name'] for x in employers],
        'description': [x['description'] for x in employers],
        'phone': [x['phone'] for x in employers],
        'url' : [x['url'] for x in employers],
        'website' : [x['website'] for x in employers],
        'logo_url' : [x['logo'] for x in employers],
        'hero_url' : [x['hero'] for x in employers],
        'video_vimeo' : [x['video_vimeo'] for x in employers],
        'video_youtube' : [x['video_youtube'] for x in employers],
        'location' : [x['location'] for x in employers],
        'address' : [x["address"] for x in employers],
        'city' : [x['city'] for x in employers],
        'state' : [x['state'] for x in employers],
        'zip' : [x['zip'] for x in employers],
        'country' : [x['country'] for x in employers],
        'created_at' : [x['created_at'] for x in employers],
        'jobs_count' : [x['active_jobs_count'] for x in employers],
        'approval_notes' : [x['custom_field_answers']['approval_notes'] if 'approval_notes' in x['custom_field_answers'].keys() else "" for x in employers],
        'approved_employer' : [x['custom_field_answers']['approved_employer'] if 'approved_employer' in x['custom_field_answers'].keys() else "" for x in employers],
        'industry_sector' : [x['custom_field_answers']['industry_sector'] if 'industry_sector' in x['custom_field_answers'].keys() else "" for x in employers],
        'relationship_to_the_vector_institute' : [x['custom_field_answers']['relationship_to_the_vector_institute'] if 'relationship_to_the_vector_institute' in x['custom_field_answers'].keys() else "" for x in employers],
    })

    return filtered_employers

def main() -> None:
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['JOBBOARD']['api_key']
    BASE_URL = 'https://canadaai.jobboard.io/api/v1/employers'
    KEY = 'employers'

    # get all employers from API
    all_employers = []
    print("### STARTING ###")
    url = BASE_URL
    employers = get_requests_loop(url, KEY, API_KEY)
    print(f'{"employers":12} | {len(employers):7}')
    all_employers.extend(employers)
    
    # filter employers and export to CSV
    print('filtering employers...')
    filtered_employers = filter_employer_list(all_employers)
    filtered_employers.to_csv('employerExport.csv', index=False)

    print("### DONE ###")
    return None

if __name__ == "__main__":
    main()