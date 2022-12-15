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

    df = pd.read_csv(file_path, index_col=False, keep_default_na=False)

    filename = os.path.basename(file_path)
    
    if 'jobs' in filename:
        jobs_mass_upload(df, KEY)
    elif 'profiles' in filename:
        profiles_mass_upload(df, KEY)
    elif 'employers' in filename:
        employers_mass_upload(df, KEY)
    else:
        raise ValueError(f'File name ({filename}) does not include one of: [jobs, profiles, employers]')

if __name__ == "__main__":
    main()
