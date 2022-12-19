# Vector-Jobboard
Working with Jobboard API to perform actions needed by Vector Institute

## Setup
In order to run the code in this repository, clone it and add a file called `config.ini`. This is where the script will look for the Jobboard API key and the GitHub Access token. The structure of the file should like the following:

```
[JOBBOARD]
api_key = <your_key_here>

[GITHUB]
access_token = <your_access_token_here>
```

### Jobboard Api Key
The API key for Jobboard can be found here: [https://canadaai.jobboard.io/admin/api_keys](https://canadaai.jobboard.io/admin/api_keys)

### Github Access Token
To obtain your github access token for the above `config.ini` file, use the followings steps:
1. Log into [github.com](https://github.com)
2. In the top right corner, click on your logo and go to **Settings**
3. At the very bottom of the left-hand side, click **Developer settings**
4. On the left-had side click **Personal access token** and then **Tokens (classic)**
5. Click **Generate new token** and then click **Generate new token (classic)**
6. Give the token whatever name you want in the **Note** section
7. Turn the **Expiration** to **No expiration**
8. Click the button to checkmark **repo** (Full control of private repositories)
9. Scroll to the bottom and click **Generate token**
10. Copy the generated token and place it in your `config.ini` file

## Usage
### Get all Exports
To obtain all the exports (jobs, profile, employer) from Jobboard, simply run the `pull_all_exports.exe` file and wait for it to finish. Once it is complete, visit whichever shared Google sheet you are interested in (in the shared Google drive). In the menu bar you will see **REFRESH HERE**, click that, followed by **Refresh Data** and wait for the script to finish running. 

### Mass Edit
TODO

## Troubleshooting
### Executable not working
If either the `pull_all_exports.exe` or `mass_edit.exe` are not working, here are the steps to re-create them:
1. Install the required python packages using the command
```
python -m pip install -r requirements.txt
```
2. Create the executable with the command (with either `pull_all_exports.py` or `mass_edit.py`)
```
pyinstaller --onefile <filename>
```