from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
from config import SCOPES


TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


def authenticate():
    creds = None

    # ── Step 1: Check for an existing saved token ──────────────────────────────
    if os.path.exists(TOKEN_FILE):
        print("[Auth] Found existing token.json — loading saved credentials...")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    else:
        print("[Auth] No token.json found — will need to log in via browser.")

    # ── Step 2: Refresh if token is expired ───────────────────────────────────
    if creds and creds.expired and creds.refresh_token:
        print("[Auth] Token is expired — refreshing automatically...")
        try:
            creds.refresh(Request())
            print("[Auth] Token refreshed successfully.")
            _save_token(creds)
        except Exception as e:
            print(f"[Auth] Could not refresh token: {e}")
            print("[Auth] Will re-authenticate via browser...")
            creds = None  # force re-login below

    # ── Step 3: Full browser OAuth flow if no valid creds ─────────────────────
    if not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(
                f"\n[Auth] ERROR: '{CREDENTIALS_FILE}' not found!\n"
                "  → Go to https://console.cloud.google.com\n"
                "  → APIs & Services → Credentials → Create OAuth 2.0 Client ID\n"
                "  → Download and save as credentials.json in this folder.\n"
            )

        print("\n[Auth] ─────────────────────────────────────────────────────")
        print("[Auth]  Opening your browser for Gmail login...")
        print("[Auth]  1. Choose your Google account")
        print("[Auth]  2. Click  'Continue'  (even if it says 'unverified app')")
        print("[Auth]  3. Click  'Allow'  to grant Gmail read access")
        print("[Auth] ─────────────────────────────────────────────────────\n")

        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES
        )

        # open_browser=True forces the browser to open automatically
        creds = flow.run_local_server(port=0, open_browser=True)

        print("\n[Auth] ✅ Authorization successful! Saving token for future runs...")
        _save_token(creds)

    print(f"[Auth] ✅ Authenticated. Token valid: {creds.valid}")
    return creds


def _save_token(creds):
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())
    print(f"[Auth] Token saved to {TOKEN_FILE}")