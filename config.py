import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gmail OAuth scope — read-only access to your inbox
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

SCHEDULE_HOURS = 3