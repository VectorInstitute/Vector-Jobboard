import requests
import json
from typing import *
import pandas as pd

MAX_GET = 50

# Calculate the target file size in bytes (50 MB)
target_file_size = 50 * 1024 * 1024

# Splitting data into chunks based on size
def split_dataframe(dataframe, chunk_size):
    chunks = []
    current_chunk = pd.DataFrame(columns=dataframe.columns)
    current_size = 0

    for index, row in dataframe.iterrows():
        row_size = row.memory_usage(deep=True)
        if current_size + row_size > chunk_size:
            chunks.append(current_chunk)
            current_chunk = pd.DataFrame(columns=dataframe.columns)
            current_size = 0

        current_chunk = current_chunk.append(row)
        current_size += row_size

    if not current_chunk.empty:
        chunks.append(current_chunk)

    return chunks

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
