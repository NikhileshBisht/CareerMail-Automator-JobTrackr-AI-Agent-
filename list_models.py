import google.generativeai as genai
import os

# Try to read from .env manually
api_key = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.split("=", 1)[1].strip()

if not api_key:
    print("GEMINI_API_KEY not found in .env")
else:
    genai.configure(api_key=api_key)
    try:
        print("Listing available models containing 'flash'...")
        for m in genai.list_models():
            if 'flash' in m.name.lower() and 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
