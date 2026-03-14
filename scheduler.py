import schedule
import time
from datetime import datetime, timedelta
from gmail_auth import authenticate
from gmail_reader import fetch_emails
from llm_processor import process_emails_with_llm
from db import upsert_job
from config import SCHEDULE_HOURS

# Track the last run time to define the window
last_run_time = datetime.now()

def run_agent():
    global last_run_time
    current_time = datetime.now()
    
    # window is (last_run_time, current_time)
    print(f"\n[Bot] Cycle started at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[Bot] Fetching emails between {last_run_time} and {current_time}...")
    
    try:
        creds = authenticate()
        raw_emails = fetch_emails(creds, start_time=last_run_time, end_time=current_time)
        
        if not raw_emails:
            print("[Bot] No new emails found in this window.")
        else:
            print(f"[Bot] Found {len(raw_emails)} emails. Sending to LLM...")
            processed_results = process_emails_with_llm(raw_emails)
            
            for res in processed_results:
                upsert_job(
                    company=res.get('company'),
                    job_id=res.get('job_id'),
                    description=res.get('description'),
                    status=res.get('status'),
                    action=res.get('action')
                )
        
        # Update last run time for the next cycle
        last_run_time = current_time
        print(f"[Bot] Cycle complete. Next run in {SCHEDULE_HOURS} hours.")
        
    except Exception as e:
        print(f"[Bot] ERROR during cycle: {e}")

# Schedule the job - this will trigger every 3 hours after the app starts
# But the first execution will be handled in start()
schedule.every(SCHEDULE_HOURS).hours.do(run_agent)

def start():
    print(f"[Bot] Starting Gmail Job Tracker (3-hour cycles)...")
    
    global last_run_time
    # Set the start time to 3 hours ago so the immediate first run covers that window
    last_run_time = datetime.now() - timedelta(hours=SCHEDULE_HOURS)
    
    print(f"[Bot] App started. Initial fetch window: {last_run_time.strftime('%H:%M:%S')} to {datetime.now().strftime('%H:%M:%S')}")
    
    # Run the agent immediately to process the last 3 hours of emails
    run_agent()
    
    print(f"[Bot] Monitoring active. Continuous 3-hour cycles will follow.")
    
    while True:
        schedule.run_pending()
        time.sleep(10)