import configparser
from utils import get_requests_loop
import os
import pandas as pd
from typing import *

def filter_profile_list(profiles: list) -> pd.DataFrame:
    filtered_profiles = pd.DataFrame({
        'id' : [x['id'] for x in profiles],
        'email' : [x['email'] for x in profiles],
        'fname': [x['fname'] for x in profiles],
        'lname': [x['lname'] for x in profiles],
        'profile_image_url': [x['image']['url'] for x in profiles],
        'label' : [x['label'] for x in profiles],
        'summary' : [x['summary'] for x in profiles],
        'phone' : [x['phone'] for x in profiles],
        'video' : ["" for x in profiles],
        'website' : [x['website'] for x in profiles],
        'facebook' : [x['facebook'] for x in profiles],
        'linkedin' : [x['linkedin'] for x in profiles],
        'twitter' : [x['twitter'] for x in profiles],
        'hidden' : [x['hidden'] for x in profiles],
        'confidential' : [x['confidential'] for x in profiles],
        'resume' : [x['resume_url'] if 'resume_url' in x.keys() else "" for x in profiles],
        'city' : [x['city'] for x in profiles],
        'state' : [x['state'] for x in profiles],
        'zip' : [x['zip'] for x in profiles],
        'country' : [x['country'] for x in profiles],
        'provider' : [x['provider'] for x in profiles],
        'created_at' : [x['created_at'] for x in profiles],
        'last_sign_in_at' : [x['last_sign_in_at'] for x in profiles],
        'open_to_remote' : [x['open_to_remote'] for x in profiles],
        'open_to_relocation' : [x['open_to_relocation'] for x in profiles],
        'vector_affiliation_categories' : [x['custom_field_answers']['vector_affiliation_categories'] if 'vector_affiliation_categories' in x['custom_field_answers'].keys() else "" for x in profiles],
        'approved_profile' : [x['custom_field_answers']['approved_profile'] if 'approved_profile' in x['custom_field_answers'].keys() else "" for x in profiles],
        'vector_affiliation' : [x['custom_field_answers']['vector_affiliation'] if 'vector_affiliation' in x['custom_field_answers'].keys() else "" for x in profiles],
        'if_you_are_associated_with_a_vector_faculty_or_faculty_affiliate_please_state_their_name_here' : [x['custom_field_answers']['if_you_are_associated_with_a_vector_faculty_or_faculty_affiliate_please_state_their_name_here'] if 'if_you_are_associated_with_a_vector_faculty_or_faculty_affiliate_please_state_their_name_here' in x['custom_field_answers'].keys() else "" for x in profiles],
        'what_is_your_estimated_graduation_date_if_still_studying' : [x['custom_field_answers']['what_is_your_estimated_graduation_date_if_still_studying'] if 'what_is_your_estimated_graduation_date_if_still_studying' in x['custom_field_answers'].keys() else "" for x in profiles],
        'if_you_chose_otherunsure_please_explain' : [x['custom_field_answers']['if_you_chose_otherunsure_please_explain'] if 'if_you_chose_otherunsure_please_explain' in x['custom_field_answers'].keys() else "" for x in profiles],
        'preferred_pronoun' : [x['custom_field_answers']['preferred_pronoun'] if 'preferred_pronoun' in x['custom_field_answers'].keys() else "" for x in profiles],
        'verified_linkedin_url' : [x['custom_field_answers']['verified_linkedin_url'] if 'verified_linkedin_url' in x['custom_field_answers'].keys() else "" for x in profiles],
        'what_are_your_primary_areas_of_research_interest_please_select_the_top_3_from_the_list_below' : [", ".join(x['custom_field_answers']['what_are_your_primary_areas_of_research_interest_please_select_the_top_3_from_the_list_below']) if 'what_are_your_primary_areas_of_research_interest_please_select_the_top_3_from_the_list_below' in x['custom_field_answers'].keys() else "" for x in profiles],
        'what_is_your_highest_level_of_education_note_if_currently_enrolled_please_include_this_level' : [x['custom_field_answers']['what_is_your_highest_level_of_education_note_if_currently_enrolled_please_include_this_level'] if 'what_is_your_highest_level_of_education_note_if_currently_enrolled_please_include_this_level' in x['custom_field_answers'].keys() else "" for x in profiles],
        'what_is_your_level_of_experience_this_could_be_through_internships_phd_research_experience_or_industry_experience_post_graduation' : [x['custom_field_answers']['what_is_your_level_of_experience_this_could_be_through_internships_phd_research_experience_or_industry_experience_post_graduation'] if 'what_is_your_level_of_experience_this_could_be_through_internships_phd_research_experience_or_industry_experience_post_graduation' in x['custom_field_answers'].keys() else "" for x in profiles],
        'what_is_your_program_of_study' : [x['custom_field_answers']['what_is_your_program_of_study'] if 'what_is_your_program_of_study' in x['custom_field_answers'].keys() else "" for x in profiles],
        'what_sectors_interest_you' : [", ".join(x['custom_field_answers']['what_sectors_interest_you']) if 'what_sectors_interest_you' in x['custom_field_answers'].keys() else "" for x in profiles],
        'opportunities_you_are_looking_for' : [", ".join(x['custom_field_answers']['opportunities_you_are_looking_for']) if 'opportunities_you_are_looking_for' in x['custom_field_answers'].keys() else "" for x in profiles],
        'what_types_of_roles_are_you_looking_for' : [", ".join(x['custom_field_answers']['what_types_of_roles_are_you_looking_for']) if 'what_types_of_roles_are_you_looking_for' in x['custom_field_answers'].keys() else "" for x in profiles],
        'which_ontario_university_did_you_attend_most_recent_education' : [x['custom_field_answers']['which_ontario_university_did_you_attend_most_recent_education'] if 'which_ontario_university_did_you_attend_most_recent_education' in x['custom_field_answers'].keys() else "" for x in profiles],
        'Data Use Terms' : [x['consents'][1]['consented'] for x in profiles],
        'Opt In' : [x['consents'][2]['consented'] for x in profiles],
        'Privacy Policy' : [x['consents'][0]['consented'] for x in profiles],
        'Privacy Statement' : [x['consents'][3]['consented'] for x in profiles],
    })

    return filtered_profiles

def main() -> None:
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['JOBBOARD']['api_key']
    BASE_URL = 'https://canadaai.jobboard.io/api/v1/profiles'
    KEY = 'profiles'

    # get all profiles from API
    all_profiles = []
    print("### STARTING ###")
    url = BASE_URL
    profiles = get_requests_loop(url, KEY, API_KEY)
    print(f'{"profiles":12} | {len(profiles):7}')
    all_profiles.extend(profiles)
    
    # filter profiles and export to CSV
    print('filtering profiles...')
    filtered_profiles = filter_profile_list(all_profiles)
    filtered_profiles.to_csv('profileExport.csv', index=False)

    # push CSV to GitHub
    print('pushing to GitHub...')
    commands = [
        "git fetch --all",
        "git add -f profileExport.csv",
        "git stash push -m export profileExport.csv",
        "git checkout gh-pages",
        "git pull origin gh-pages --rebase",
        "git cherry-pick -n -m1 -Xtheirs stash",
        'git commit -m "Update profile export"',
        'git push',
        'git checkout main'
    ]

    for com in commands:
        os.system(com)

    print("### DONE ###")
    return None

if __name__ == "__main__":
    main()