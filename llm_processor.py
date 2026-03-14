import google.generativeai as genai
import json
import os
import pandas as pd
from config import GEMINI_API_KEY
from db import JOBS_FILE

def process_emails_with_llm(emails):
    """
    Sends emails to Gemini to filter job-related ones and classify them.
    Also compares with existing jobs.csv to determine the action (insert/update/skip).
    """
    if not emails:
        print("[LLM] No emails to process.")
        return []

    if not GEMINI_API_KEY:
        print("[LLM] ERROR: GEMINI_API_KEY not found in configuration.")
        return []

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')

    # Load existing jobs for context
    existing_jobs_str = ""
    if os.path.exists(JOBS_FILE):
        df = pd.read_csv(JOBS_FILE)
        existing_jobs_str = df.to_csv(index=False)

    # Format emails for prompt
    emails_data = []
    for sender, subject, snippet in emails:
        emails_data.append({
            "sender": sender,
            "subject": subject,
            "snippet": snippet
        })

    prompt = f"""
    You are an AI assistant helping to track job applications.
    Here is a CSV of existing job applications:
    {existing_jobs_str}

    Here are some new emails fetched from Gmail:
    {json.dumps(emails_data, indent=2)}

    Your task:
    1. Filter out any emails that are NOT related to job applications (e.g., newsletters, promotions, personal emails).
    2. For job-related emails, extract:
       - 'company': The company name.
       - 'job_id': A unique identifier if available (often found in subject or body), else null.
       - 'description': A brief summary of the email content.
       - 'status': The current state (e.g., 'Applied', 'Interviewing', 'Rejected', 'Offer', 'Accepted').
    3. Compare with the existing jobs. Based on (company, job_id), decide the 'action':
       - 'insert': This is a new job application.
       - 'update': The job exists, but the status or info has changed.
       - 'skip': The job exists and the info is already up to date.

    Return the results ONLY as a JSON array of objects with these keys: 
    "company", "job_id", "description", "status", "action".
    Do not include any other text or markdown formatting.
    """

    print("[LLM] Sending emails to Gemini for processing...")
    try:
        response = model.generate_content(prompt)
        # Handle potential markdown wrappers in response
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        results = json.loads(response_text)
        return results
    except Exception as e:
        print(f"[LLM] ERROR during processing: {e}")
        return []
