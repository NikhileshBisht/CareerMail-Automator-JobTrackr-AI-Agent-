from googleapiclient.discovery import build


def fetch_emails(creds, start_time=None, end_time=None):
    print("[Gmail] Connecting to Gmail API...")
    service = build('gmail', 'v1', credentials=creds)

    query = "application OR interview OR rejected"
    if start_time and end_time:
        # Convert to UNIX timestamps
        after_ts = int(start_time.timestamp())
        before_ts = int(end_time.timestamp())
        query += f" after:{after_ts} before:{before_ts}"
        print(f"[Gmail] Searching between {start_time} and {end_time}...")
    else:
        print("[Gmail] Searching for job-related emails (all time or default limit)...")

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=50
    ).execute()

    messages = results.get('messages', [])
    print(f"[Gmail] Found {len(messages)} matching message(s).")

    emails = []

    for i, msg in enumerate(messages, 1):
        message = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(no subject)")
        sender  = next((h['value'] for h in headers if h['name'] == 'From'),    "(unknown sender)")
        snippet = message.get('snippet', '')

        print(f"[Gmail]  [{i}/{len(messages)}] From: {sender[:50]} | Subject: {subject[:60]}")
        emails.append((sender, subject, snippet))

    return emails