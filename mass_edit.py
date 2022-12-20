import configparser
import os
import tkinter as tk
from tkinter import filedialog

import pandas as pd

from mass_upload import *


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    KEY = config['JOBBOARD']['api_key']

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    df = pd.read_csv(
        file_path,
        index_col=False,
        keep_default_na=False,
        true_values = ['TRUE'],
        false_values = ['FALSE']
    )

    filename = os.path.basename(file_path)
    
    if filename == 'Job Export - Sheet1.csv':
        jobs_mass_upload(df, KEY)
    elif filename == 'Profile Export - Sheet1.csv':
        profiles_mass_upload(df, KEY)
    elif filename == 'Employer Export - Sheet1.csv':
        employers_mass_upload(df, KEY)
    else:
        raise ValueError(f'File name ({filename}) does not include one of: [jobs, profiles, employers]')

if __name__ == "__main__":
    main()
