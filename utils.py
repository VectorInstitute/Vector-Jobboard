import requests
import json
from typing import *

MAX_GET = 500

def get_requests_loop(url: str, key: str, api_key: str) -> list:
    all_responses = []

    headers = {
        "accept": "application/json",
        "JobBoardioURL": "https://talenthub.vectorinstitute.ai/",
        "X-Api-Key": api_key
    }

    still_jobs = True
    i = 1
    while still_jobs:
        extend_url = url + f'&page={i}&per_page={MAX_GET}' if '?' in url else \
            url + f'?page={i}&per_page={MAX_GET}'
        
        response = requests.get(extend_url, timeout=None, headers = headers)
        
        if response.status_code != 200:
            print(extend_url)
            print(response)
            raise ValueError(f'Response is bad:\n{response}')
            
        
        values = json.loads(response.text)[key]
        all_responses.extend(values)

        if len(values) == 0:
            still_jobs = False
        i += 1

    return all_responses
