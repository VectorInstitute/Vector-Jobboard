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

## Troubleshooting
### Executable not working
If either the `pull_all_exports.exe` or `mass_edit.exe` are not working, here are the steps to re-create them:
1. Install the required python packages using the command
```
python -m pip install -r requirements.txt
```
2. Create the executable with the command (with either `pull_all_exports.exe` or `mass_edit.exe`)
```
pyinstaller --onefile <filename>
```