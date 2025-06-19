import streamlit as st
from utils.extract_text import extract_text_from_pdf
from utils.gemini_client import extract_key_info, generate_workflow, estimate_value, generate_lease_from_prompt
from utils.visualize_workflow import render_workflow
import os

# Configure page settings
st.set_page_config(page_title="CRE Orchestrator AI", layout="wide")

# Header section with explanation
st.title("🏢 CRE Orchestrator AI")
st.markdown("""
### How This App Works
This application helps commercial real estate professionals analyze lease agreements and build automated workflows.

**Process Flow:**
1. **Input** - Choose a lease agreement (generate new, upload, or use sample)
2. **Analysis** - AI extracts key lease information
3. **Workflow Design** - Generate automation steps across multiple systems
4. **Value Assessment** - Calculate ROI and business impact

Each step builds on the previous one to create a complete solution.
""")

# Create a sidebar for navigation
with st.sidebar:
    st.title("Navigation")
    
    # Add more detailed explanations for each option
    option = st.radio(
        "Choose your starting point:",
        ["Generate a new lease", 
         "Upload existing lease",
         "Use sample lease"]
    )
    
    # Explanation of the selected option
    if option == "Generate a new lease":
        st.info("""
        **Generate New Lease:** 
        Describe your lease terms in plain language, and the AI will create a full legal agreement, then analyze it.
        
        **Example:** "Office space in Manhattan, 3-year term, $5000/month, 60-day termination clause"
        """)
    elif option == "Upload existing lease":
        st.info("""
        **Upload Existing Lease:** 
        Upload your PDF lease document and get AI analysis on key terms, recommended workflows, and value assessment.
        """)
    else:
        st.info("""
        **Sample Lease:** 
        Use our pre-loaded sample lease to see how the analysis works without uploading your own document.
        """)
    
    st.markdown("---")
    st.markdown("### About")
    st.info("""
    **CRE Orchestrator AI** helps commercial real estate teams:
    
    • Extract key information from lease documents
    • Design automation workflows across multiple systems
    • Calculate time and cost savings from automation
    """)
    
    st.markdown("### Contact")
    email = st.text_input("Your email", placeholder="you@company.com")
    if st.button("Request Demo"):
        if email:
            st.success(f"Thanks! We'll contact {email}")
        else:
            st.error("Please enter your email")

# Main content area - Path 1: Generate lease from description
if option == "Generate a new lease":
    st.header("Generate Lease Agreement")
    st.write("📝 Describe your lease terms in simple language, and the AI will generate a complete lease agreement.")
    
    # More detailed placeholder and examples
    user_prompt = st.text_area(
        "Lease description:",
        placeholder="Example: Office space at 123 Main St, New York, NY for a 3-year term at $5,000/month with annual 3% increases, 60-day termination clause, and 2 months security deposit.",
        height=100
    )
    
    # Add explanation of what happens next
    st.caption("When you click 'Generate', the AI will create a full lease agreement based on your description, extract key information, design a workflow, and estimate value.")
    
    if user_prompt and st.button("Generate Lease Agreement"):
        # Create tabs with clearer labels
        tabs = st.tabs([
            "1️⃣ Lease Agreement", 
            "2️⃣ Key Information", 
            "3️⃣ Automation Workflow", 
            "4️⃣ Business Value"
        ])
        
        with st.spinner("Processing your request..."):
            # Generate lease
            lease_text = generate_lease_from_prompt(user_prompt)
            # Extract info
            extracted_info = extract_key_info(lease_text)
            # Generate workflow
            workflow = generate_workflow(extracted_info)
            # Estimate value
            value = estimate_value(extracted_info, workflow)
        
        # Display results in tabs with better explanations
        with tabs[0]:
            st.subheader("📄 AI-Generated Lease Agreement")
            st.info("This is the complete lease agreement generated from your description. It includes all standard clauses and terms.")
            st.code(lease_text)
            
        with tabs[1]:
            st.subheader("📌 Key Lease Information")
            st.info("The AI has extracted the most important information from the lease, including parties, dates, financial terms, and key clauses.")
            st.code(extracted_info)
            
        with tabs[2]:
            st.subheader("🛠️ Recommended Automation Workflow")
            st.info("""
            This workflow shows how to automate the lease management process across multiple systems. 
            Each step represents an action in a specific system, with arrows showing the flow between systems.
            """)
            # Display only the workflow diagram (text is in expander)
            render_workflow(workflow)
            
        with tabs[3]:
            st.subheader("💡 Business Value Assessment")
            st.info("This analysis shows the estimated ROI from implementing the proposed automation workflow.")
            st.success(value)

# Path 2: Upload existing lease
elif option == "Upload existing lease":
    st.header("Analyze Existing Lease")
    st.write("📄 Upload your lease agreement (PDF format) to extract key information and generate automation recommendations.")
    
    uploaded_file = st.file_uploader("Upload Lease (PDF format)", type="pdf")
    
    # Add explanation of what happens next
    st.caption("When you click 'Analyze', the AI will extract text from your PDF, identify key information, design a workflow, and estimate value.")
    
    if uploaded_file and st.button("Analyze Lease"):
        # Create tabs with clearer labels
        tabs = st.tabs([
            "1️⃣ Extracted Text", 
            "2️⃣ Key Information", 
            "3️⃣ Automation Workflow", 
            "4️⃣ Business Value"
        ])
        
        with st.spinner("Processing your document..."):
            # Extract text
            raw_text = extract_text_from_pdf(uploaded_file)
            # Extract info
            extracted_info = extract_key_info(raw_text)
            # Generate workflow
            workflow = generate_workflow(extracted_info)
            # Estimate value
            value = estimate_value(extracted_info, workflow)
        
        # Display results in tabs with better explanations
        with tabs[0]:
            st.subheader("📄 Extracted Lease Text")
            st.info("This is the raw text extracted from your PDF document. The AI uses this text for its analysis.")
            st.code(raw_text)
            
        with tabs[1]:
            st.subheader("📌 Key Lease Information")
            st.info("The AI has extracted the most important information from the lease, including parties, dates, financial terms, and key clauses.")
            st.code(extracted_info)
            
        with tabs[2]:
            st.subheader("🛠️ Recommended Automation Workflow")
            st.info("""
            This workflow shows how to automate the lease management process across multiple systems.
            Each step represents an action in a specific system, with arrows showing the flow between systems.
            """)
            # Display only the workflow diagram (text is in expander)
            render_workflow(workflow)
            
        with tabs[3]:
            st.subheader("💡 Business Value Assessment")
            st.info("This analysis shows the estimated ROI from implementing the proposed automation workflow.")
            st.success(value)

# Path 3: Use sample lease
else:
    st.header("Analyze Sample Lease")
    st.write("📋 Use our sample lease agreement to see how the analysis works without uploading your own document.")
    
    # Add explanation of what happens next
    st.caption("When you click 'Analyze', the AI will process our sample lease, extract key information, design a workflow, and estimate value.")
    
    if st.button("Analyze Sample Lease"):
        # Create tabs with clearer labels
        tabs = st.tabs([
            "1️⃣ Sample Lease", 
            "2️⃣ Key Information", 
            "3️⃣ Automation Workflow", 
            "4️⃣ Business Value"
        ])
        
        with st.spinner("Processing sample document..."):
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
        
        # Display results in tabs with better explanations
        with tabs[0]:
            st.subheader("📄 Sample Lease Agreement")
            st.info("This is our sample lease agreement used for demonstration purposes.")
            st.code(raw_text)
            
        with tabs[1]:
            st.subheader("📌 Key Lease Information")
            st.info("The AI has extracted the most important information from the lease, including parties, dates, financial terms, and key clauses.")
            st.code(extracted_info)
            
        with tabs[2]:
            st.subheader("🛠️ Recommended Automation Workflow")
            st.info("""
            This workflow shows how to automate the lease management process across multiple systems.
            Each step represents an action in a specific system, with arrows showing the flow between systems.
            """)
            # Display only the workflow diagram (text is in expander)
            render_workflow(workflow)
            
        with tabs[3]:
            st.subheader("💡 Business Value Assessment")
            st.info("This analysis shows the estimated ROI from implementing the proposed automation workflow.")
            st.success(value)
