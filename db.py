import csv
import os
import pandas as pd

JOBS_FILE = "jobs.csv"

def init_db():
    """
    Ensure the local CSV file exists with a header row.
    """
    file_exists = os.path.exists(JOBS_FILE)
    if not file_exists:
        with open(JOBS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["company", "job_id", "description", "status"])

def upsert_job(company, job_id, description, status, action):
    """
    Inserts or updates a job record in the CSV file.
    """
    if action == "skip":
        return

    init_db()
    df = pd.read_csv(JOBS_FILE)

    # Convert job_id to string for consistent comparison
    job_id = str(job_id) if job_id else ""
    df['job_id'] = df['job_id'].fillna('').astype(str)

    mask = (df['company'] == company) & (df['job_id'] == job_id)

    if action == "update" and mask.any():
        df.loc[mask, 'status'] = status
        df.loc[mask, 'description'] = description
        print(f"[DB] Updated: {company} | {status}")
    elif action == "insert":
        if mask.any():
             # If it exists, update it anyway to be safe, or skip if identical
             df.loc[mask, 'status'] = status
             df.loc[mask, 'description'] = description
             print(f"[DB] Match found for 'insert' - updating instead: {company} | {status}")
        else:
            new_row = pd.DataFrame([{
                "company": company,
                "job_id": job_id,
                "description": description,
                "status": status
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            print(f"[DB] Inserted: {company} | {status}")

    df.to_csv(JOBS_FILE, index=False)

def save_job(company, job_id, description, status):
    # Keeping old function for compatibility during transition if needed
    upsert_job(company, job_id, description, status, "insert")