import streamlit as st
from utils.extract_text import extract_text_from_pdf
from utils.gemini_client import extract_key_info, generate_workflow, estimate_value, generate_lease_from_prompt
from utils.visualize_workflow import render_workflow
import os

st.set_page_config(page_title="CRE Orchestrator AI", layout="wide")

# Create a sidebar for navigation
with st.sidebar:
    st.title("🏢 CRE Orchestrator AI")
    st.markdown("### Navigation")
    option = st.radio(
        "Choose your starting point:",
        ["Generate a new lease", 
         "Upload existing lease",
         "Use sample lease"]
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.info("""
    This app helps commercial real estate professionals analyze lease agreements, 
    design automation workflows, and estimate ROI of automation.
    """)
    
    st.markdown("### Contact")
    email = st.text_input("Your email", placeholder="you@company.com")
    if st.button("Request Demo"):
        if email:
            st.success(f"Thanks! We'll contact {email}")
        else:
            st.error("Please enter your email")

# Main content area
st.title("🏢 CRE Orchestrator AI")

# Path 1: Generate lease from description
if option == "Generate a new lease":
    st.header("Generate Lease Agreement")
    st.write("📝 Describe your lease terms in simple language.")
    
    user_prompt = st.text_input(
        "Lease description:",
        placeholder="e.g. Office in NYC, 3 years, $10K/month, 60-day termination"
    )
    
    if user_prompt and st.button("Generate Lease Agreement"):
        # Create tabs for results
        tabs = st.tabs(["Lease Agreement", "Key Info", "Workflow", "Value Analysis"])
        
        with st.spinner("Processing..."):
            # Generate lease
            lease_text = generate_lease_from_prompt(user_prompt)
            # Extract info
            extracted_info = extract_key_info(lease_text)
            # Generate workflow
            workflow = generate_workflow(extracted_info)
            # Estimate value
            value = estimate_value(extracted_info, workflow)
        
        # Display results in tabs
        with tabs[0]:
            st.subheader("📄 AI-Generated Lease Agreement")
            st.code(lease_text)
            
        with tabs[1]:
            st.subheader("📌 Key Lease Information")
            st.code(extracted_info)
            
        with tabs[2]:
            st.subheader("🛠️ Recommended Workflow")
            # Display only the workflow diagram (text is in expander)
            render_workflow(workflow)
            
        with tabs[3]:
            st.subheader("💡 Value Unlocked")
            st.success(value)

# Path 2: Upload existing lease
elif option == "Upload existing lease":
    st.header("Analyze Existing Lease")
    st.write("📄 Upload your lease agreement (PDF format).")
    
    uploaded_file = st.file_uploader("Upload Lease", type="pdf")
    
    if uploaded_file and st.button("Analyze Lease"):
        # Create tabs for results
        tabs = st.tabs(["Extracted Text", "Key Info", "Workflow", "Value Analysis"])
        
        with st.spinner("Processing..."):
            # Extract text
            raw_text = extract_text_from_pdf(uploaded_file)
            # Extract info
            extracted_info = extract_key_info(raw_text)
            # Generate workflow
            workflow = generate_workflow(extracted_info)
            # Estimate value
            value = estimate_value(extracted_info, workflow)
        
        # Display results in tabs
        with tabs[0]:
            st.subheader("📄 Extracted Lease Text")
            st.code(raw_text)
            
        with tabs[1]:
            st.subheader("📌 Key Lease Information")
            st.code(extracted_info)
            
        with tabs[2]:
            st.subheader("🛠️ Recommended Workflow")
            # Display only the workflow diagram (text is in expander)
            render_workflow(workflow)
            
        with tabs[3]:
            st.subheader("💡 Value Unlocked")
            st.success(value)

# Path 3: Use sample lease
else:
    st.header("Analyze Sample Lease")
    st.write("📋 Use our sample lease agreement for demonstration.")
    
    if st.button("Analyze Sample Lease"):
        # Create tabs for results
        tabs = st.tabs(["Sample Lease", "Key Info", "Workflow", "Value Analysis"])
        
        with st.spinner("Processing..."):
            # Load sample lease
            default_file_path = os.path.join("utils", "rentalagreement.txt")
            with open(default_file_path, "r") as file:
                raw_text = file.read()
                
            # Extract info
            extracted_info = extract_key_info(raw_text)
            # Generate workflow
            workflow = generate_workflow(extracted_info)
            # Estimate value
            value = estimate_value(extracted_info, workflow)
        
        # Display results in tabs
        with tabs[0]:
            st.subheader("📄 Sample Lease Agreement")
            st.code(raw_text)
            
        with tabs[1]:
            st.subheader("📌 Key Lease Information")
            st.code(extracted_info)
            
        with tabs[2]:
            st.subheader("🛠️ Recommended Workflow")
            # Display only the workflow diagram (text is in expander)
            render_workflow(workflow)
            
        with tabs[3]:
            st.subheader("💡 Value Unlocked")
            st.success(value)
