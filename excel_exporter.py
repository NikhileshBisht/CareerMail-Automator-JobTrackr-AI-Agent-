import os
import pandas as pd
from db import JOBS_FILE


def export_excel():

    if not os.path.exists(JOBS_FILE):
        # Nothing to export yet
        return

    df = pd.read_csv(JOBS_FILE)

    df.to_excel("jobs.xlsx", index=False)