import requests
import json
from tqdm import tqdm
from datetime import date
import pandas as pd
import sys

def main():

    column_names = ["Email", "fname", "lname", "profile_image_url", "label", "summary", "phone", "linkedin", "hidden", "confidential", "city", "state", "zip", "country", "provider", "last_sign_in_at", "open_to_remote", "open_to_relocation", "vector_affiliation", "approved_profile", "vector_affiliation_categories", "what_is_your_estimated_graduation_date_if_still_studying", "preferred_pronoun", "verified_linkedin_url", "what_is_your_highest_level_of_education_note_if_currently_enrolled_please_include_this_level"]
    main_c = ["Email", "fname", "lname", "profile_image_url", "label", "summary", "phone", "linkedin", "hidden", "confidential", "city", "state", "zip", "country", "provider", "last_sign_in_at", "open_to_remote", "open_to_relocation"]
    custom_c = ["vector_affiliation", "approved_profile", "vector_affiliation_categories", "what_is_your_estimated_graduation_date_if_still_studying", "preferred_pronoun", "verified_linkedin_url", "what_is_your_highest_level_of_education_note_if_currently_enrolled_please_include_this_level"]
    df = pd.DataFrame(columns = column_names)

    url = "https://canadaai.jobboard.io/api/v1/profiles"
    API_KEY = sys.argv[1]

    headers = {
        "Accept": "application/json",
        "JobBoardioURL": "https://talenthub.vectorinstitute.ai/",
        "X-Api-Key" : API_KEY
    }

    page = 1
    per_page = 200
    querystring = {"page":str(page),"per_page":str(per_page)}

    print("Fetching all profiles .... ")

    response = requests.request("GET", url, headers=headers, params = querystring)

    data = json.loads(response.text)

    while len(data['profiles']) > 0:
        for i in tqdm(range(len(data['profiles']))):
            if data['profiles'][i]['last_sign_in_at'] != None:
                dt = data['profiles'][i]['last_sign_in_at'].split('T')[0].split('-')
                for col in main_c:
                    if col not in data['profiles'][i].keys():
                        data['profiles'][i][col] = 'NULL'
                for col in custom_c:
                    if col not in data['profiles'][i]['custom_field_answers']:
                        data['profiles'][i]['custom_field_answers'][col] = "NULL"
                signin_date = date(int(dt[0]), int(dt[1]), int(dt[2]))
                today = date.today()
                diff = today - signin_date
                if(diff.days >= 180):
                    df2 = pd.Series(data = {"Email" : data['profiles'][i]['email'], "fname" : data['profiles'][i]['fname'], "lname" : data['profiles'][i]['lname'], "profile_image_url": data['profiles'][i]['image']['url'], "label": data['profiles'][i]['label'], "summary": data['profiles'][i]['summary'], "phone": data['profiles'][i]['phone'], "linkedin": data['profiles'][i]['linkedin'], "hidden": data['profiles'][i]['hidden'], "confidential": data['profiles'][i]['confidential'], "city": data['profiles'][i]['city'], "state": data['profiles'][i]['state'], "zip": data['profiles'][i]['zip'], "country": data['profiles'][i]['country'], "provider": data['profiles'][i]['provider'], "last_sign_in_at": data['profiles'][i]['last_sign_in_at'], "open_to_remote": data['profiles'][i]['open_to_remote'], "open_to_relocation": data['profiles'][i]['open_to_relocation'], "vector_affiliation": data['profiles'][i]['custom_field_answers']['vector_affiliation'], "approved_profile":data['profiles'][i]['custom_field_answers']['approved_profile'], "vector_affiliation_categories":data['profiles'][i]['custom_field_answers']['vector_affiliation'], "what_is_your_estimated_graduation_date_if_still_studying":data['profiles'][i]['custom_field_answers']['what_is_your_estimated_graduation_date_if_still_studying'], "preferred_pronoun":data['profiles'][i]['custom_field_answers']['preferred_pronoun'], "verified_linkedin_url":data['profiles'][i]['custom_field_answers']['verified_linkedin_url'], "what_is_your_highest_level_of_education_note_if_currently_enrolled_please_include_this_level":data['profiles'][i]['custom_field_answers']['what_is_your_highest_level_of_education_note_if_currently_enrolled_please_include_this_level']}, name = data['profiles'][i]['id'])
                    df = df.append(df2, ignore_index = False)

        page += 1
        querystring = {"page":str(page),"per_page":str(per_page)}
        print("Fetching all profiles .... ")
        response = requests.request("GET", url, headers=headers, params = querystring)
        data = json.loads(response.text)

    df.to_csv("OldProfiles_ProfilesExport.csv")

if __name__ == "__main__":
    main()