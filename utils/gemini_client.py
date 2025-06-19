import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the base URL and model name
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MODEL_NAME = "gemini-2.0-flash"
API_KEY = os.getenv("GEMINI_API_KEY")

def make_gemini_request(prompt):
    """
    Make a request to the Gemini API with the given prompt.
    
    Args:
        prompt (str): The prompt to send to the Gemini API
        
    Returns:
        str: The text response from the Gemini API
    """
    url = f"{BASE_URL}/{MODEL_NAME}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Error making request to Gemini API: {e}")
        return f"Error: {str(e)}"

def generate_lease_from_prompt(prompt):
    """Generate a lease agreement from a simple description"""
    lease_prompt = f"""
You're a commercial real estate legal assistant. Based on this description, generate a realistic lease agreement:

{prompt}

Format as a standard lease agreement with all the typical sections and clauses.
"""
    return make_gemini_request(lease_prompt)

def extract_key_info(document_text):
    """Extract key information from a lease document"""
    prompt = f"""
You're an AI assistant for commercial real estate.

Extract key info from the following lease agreement:
- Property address
- Parties involved
- Lease term and dates
- Rent details
- Any renewal or termination clauses
- Any key deadlines

Document:
{document_text}
"""
    return make_gemini_request(prompt)

def generate_workflow(extracted_info):
    """Generate a workflow based on extracted lease information"""
    prompt = f"""
Based on this lease agreement info:

{extracted_info}

Suggest a 4–6 step automation workflow using tools like:
- Salesforce
- DocuSign
- Google Drive
- Slack

Include the purpose of each step.
Format as a numbered list with clear step titles.
"""
    return make_gemini_request(prompt)

def estimate_value(extracted_info, workflow_text):
    """Estimate the business value of the proposed workflow"""
    prompt = f"""
Based on the following workflow:

{workflow_text}

Estimate:
- Hours saved
- Risk or error avoided
- Which teams benefit most
Return in 3 bullet points.
"""
    return make_gemini_request(prompt)
