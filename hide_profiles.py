import pandas as pd
import json
import requests
import sys

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
    x = df.iloc[:, 0].values
    headers = {
        "Accept": "application/json",
        "JobBoardioURL": "https://talenthub.vectorinstitute.ai/",
        "X-Api-Key" : JOBBOARD_API_KEY
    }

    for ID in range(len(x)):
        url = "https://canadaai.jobboard.io/api/v1/profiles/" + str(x[ID])

        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)
        if data['profile']['hidden'] or data['profile']['hidden'] == 'True':
            continue
        payload = {"hidden": True}
        response = requests.request("PATCH", url, json=payload, headers=headers)
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)

if __name__ == "__main__":
    main()