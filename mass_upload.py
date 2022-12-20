import numpy as np
import pandas as pd
import requests
import json

CUSTOM_PROFILE_FIELDS = [
    'vector_affiliation_categories',
    'approved_profile',
    'vector_affiliation',
    'if_you_are_associated_with_a_vector_faculty_or_faculty_affiliate_please_state_their_name_here',
    'what_is_your_estimated_graduation_date_if_still_studying',
    'if_you_chose_otherunsure_please_explain',
    'preferred_pronoun',
    'verified_linkedin_url',
    'what_are_your_primary_areas_of_research_interest_please_select_the_top_3_from_the_list_below',
    'what_is_your_highest_level_of_education_note_if_currently_enrolled_please_include_this_level',
    'what_is_your_level_of_experience_this_could_be_through_internships_phd_research_experience_or_industry_experience_post_graduation',
    'what_is_your_program_of_study',
    'what_sectors_interest_you',
    'opportunities_you_are_looking_for',
    'what_types_of_roles_are_you_looking_for',
    'which_ontario_university_did_you_attend_most_recent_education',
]

CUSTOM_JOB_FIELDS = [
    'company_size',
    'email_applications_or_application_click_through',
    'job_industry',
    'level_of_experience',
    'minimum_degree_level',
    'new_posting_or_repost'
]

CUSTOM_EMPLOYER_FIELDS = [
    'approval_notes',
    'approved_employer',
    'industry_sector',
    'relationship_to_the_vector_institute',
]

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super(NpEncoder, self).default(obj)

def jobs_mass_upload(df: pd.DataFrame, key: str) -> None:
    # TODO: fix this because it's not working
    
    REQUIRED_FIELDS = [
        'id',
        'title',
        'company',
        'location',
        'description',
        'contact_email',
        'apply_email',
        'apply_url',
    ]
    
    
    url = "https://canadaai.jobboard.io/api/v1/jobs/"
    headers = {
        "X-Api-Key": key,
        'accept': 'text/plain',
        "JobBoardioURL": "https://talenthub.vectorinstitute.ai/",
        'content-type' : 'application/json'
}   

    fields = df.columns

    for field in REQUIRED_FIELDS:
        if not any(field == fields):
            raise ValueError(f'Did not supply all required fields: {field}')

    for i in range(df.shape[0]):
        token = df['id'][i]
        curr_url = url + str(token)
        payload = dict()

        for field in fields:
            if field == 'id':
                continue
            if field in CUSTOM_JOB_FIELDS:
                if not ('custom_field_answers' in payload.keys()):
                    payload['custom_field_answers'] = {}
                payload['custom_field_answers'][field] = df[field][i]
            else:
                payload[field] = df[field][i]
        r = requests.request(
            "PATCH",
            curr_url,
            data = json.dumps(payload, cls = NpEncoder),
            headers=headers
        )

    return None

def profiles_mass_upload(df: pd.DataFrame, key: str) -> None:
    
    url = "https://canadaai.jobboard.io/api/v1/profiles/"
    headers = {
        "X-Api-Key": key,
        'accept': 'text/plain',
        "JobBoardioURL": "https://talenthub.vectorinstitute.ai/",
        'content-type' : 'application/json'
    }

    fields = df.columns

    for i in range(df.shape[0]):
        token = df['id'][i]
        curr_url = url + str(token)
        payload = dict()

        for field in fields:
            if field == 'id':
                continue
            if field in CUSTOM_PROFILE_FIELDS:
                if not ('custom_field_answers' in payload.keys()):
                    payload['custom_field_answers'] = {}
                payload['custom_field_answers'][field] = df[field][i]
            else:
                payload[field] = df[field][i]
        r = requests.request(
            "PATCH",
            curr_url,
            data = json.dumps(payload, cls = NpEncoder),
            headers=headers
        )
   
    return None

def employers_mass_upload(df: pd.DataFrame, key: str) -> None:

    url = "https://canadaai.jobboard.io/api/v1/employers/"
    headers = {
        "X-Api-Key": key,
        'accept': 'text/plain',
        "JobBoardioURL": "https://talenthub.vectorinstitute.ai/",
        'content-type' : 'application/json'
    }

    fields = df.columns

    for i in range(df.shape[0]):
        token = df['id'][i]
        curr_url = url + str(token)
        payload = dict()

        for field in fields:
            if field == 'id':
                continue
            if field in CUSTOM_EMPLOYER_FIELDS:
                if not ('custom_field_answers' in payload.keys()):
                    payload['custom_field_answers'] = {}
                payload['custom_field_answers'][field] = df[field][i]
            else:
                payload[field] = df[field][i]
        r = requests.request(
            "PATCH",
            curr_url,
            data = json.dumps(payload, cls = NpEncoder),
            headers=headers
        )

    return None