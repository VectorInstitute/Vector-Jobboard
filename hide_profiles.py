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
    hidden_count = 0
    already_hidden_count = 0
    failed_count = 0
    for ID in range(len(x)):
        url = "https://canadaai.jobboard.io/api/v1/profiles/" + str(x[ID])
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)
        try:
            if data['profile']['hidden'] or data['profile']['hidden'] == 'True':
                already_hidden_count += 1
                continue
        except:
            failed_count += 1
            continue
        payload = {"hidden": True}
        response = requests.request("PATCH", url, json=payload, headers=headers)
        if response.status_code >= 200 and response.status_code < 300:
            hidden_count += 1
        else:
            failed_count += 1
    print("Hidden:", hidden_count)
    print("Already hidden:", already_hidden_count)
    print("Failed:", failed_count)

if __name__ == "__main__":
    main()
