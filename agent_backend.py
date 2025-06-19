import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MODEL_NAME = "gemini-2.0-flash"

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

def analyze_lease_document(document_text):
    """
    Analyze a lease document using a series of Gemini API calls that mimic an agent workflow.
    
    Args:
        document_text (str): The raw text of the lease document
        
    Returns:
        dict: A dictionary containing the extracted info, workflow, and value analysis
    """
    # Step 1: Extract key information (Lease Analyst role)
    lease_analysis_prompt = f"""
    You are a Lease Analyst specializing in commercial real estate documents.
    
    Analyze this lease document and extract key information:
    - Property address
    - Parties involved (landlord and tenant)
    - Lease term and important dates
    - Rent details and payment schedule
    - Renewal and termination clauses
    - Any key deadlines or milestones
    
    Format your response as a structured summary.
    
    Document: {document_text}
    """
    
    extracted_info = make_gemini_request(lease_analysis_prompt)
    
    # Step 2: Generate workflow recommendations (Workflow Architect role)
    workflow_prompt = f"""
    You are a Workflow Architect specializing in commercial real estate automation.
    
    Based on this lease information:
    {extracted_info}
    
    Design an automation workflow with 4-6 steps using tools like:
    - Salesforce
    - DocuSign
    - Google Drive
    - Slack
    
    For each step, explain its purpose and how it helps automate the lease management process.
    Format as a numbered list with clear step titles and descriptions.
    """
    
    workflow = make_gemini_request(workflow_prompt)
    
    # Step 3: Estimate business value (Value Analyst role)
    value_prompt = f"""
    You are a Value Analyst specializing in ROI of automation in commercial real estate.
    
    Based on the lease information:
    {extracted_info}
    
    And the proposed workflow:
    {workflow}
    
    Estimate:
    - Hours saved by automating manual tasks
    - Risk or errors avoided through automation
    - Which teams benefit most from this automation
    
    Format your response as 3 bullet points.
    """
    
    value = make_gemini_request(value_prompt)
    
    # Return results in the same format as the agent-based approach
    return {
        "extracted_info": extracted_info,
        "workflow": workflow,
        "value": value
    }

if __name__ == "__main__":
    # Simple test for the analyze_lease_document function
    sample_text = "This is a sample lease agreement between Landlord A and Tenant B for property at 123 Main St."
    results = analyze_lease_document(sample_text)
    print("EXTRACTED INFO:")
    print(results["extracted_info"])
    print("\nWORKFLOW:")
    print(results["workflow"])
    print("\nVALUE:")
    print(results["value"])
