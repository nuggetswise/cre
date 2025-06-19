import streamlit as st
from utils.gemini_client import extract_key_info, generate_workflow, estimate_value, generate_lease_from_prompt
from utils.visualize_workflow import render_workflow
import os

st.set_page_config(page_title="CRE Orchestrator AI (Prompt Mode)", layout="centered")
st.title("🏢 CRE Orchestrator AI")
st.markdown("Just describe your lease deal — and let AI create the agreement, extract key info, generate a workflow, and show the value.")

user_prompt = st.text_input(
    "📝 Describe your lease in one sentence:",
    placeholder="e.g. Leasing office in NYC for 3 years at $10K/month with a 60-day termination"
)

# Load default document if no user input
if not user_prompt:
    default_file_path = os.path.join("utils", "rentalagreement.txt")
    with open(default_file_path, "r") as file:
        lease_text = file.read()
    st.subheader("📄 Default Lease Agreement")
    st.code(lease_text)

    with st.spinner("🔍 Extracting key info..."):
        extracted_info = extract_key_info(lease_text)
    st.subheader("📌 Key Lease Info")
    st.code(extracted_info)

    with st.spinner("🔧 Generating workflow..."):
        workflow = generate_workflow(extracted_info)
    st.subheader("🛠️ Recommended Workflow")
    st.code(workflow)

    st.subheader("🔄 Workflow Diagram")
    render_workflow(workflow)

    with st.spinner("📈 Estimating value..."):
        value = estimate_value(extracted_info, workflow)
    st.subheader("💡 Value Unlocked")
    st.success(value)

if user_prompt and st.button("Generate Lease + Workflow"):
    with st.spinner("✍️ Generating lease..."):
        lease_text = generate_lease_from_prompt(user_prompt)

    st.subheader("📄 AI-Generated Lease Agreement")
    st.code(lease_text)

    with st.spinner("🔍 Extracting key info..."):
        extracted_info = extract_key_info(lease_text)
    st.subheader("📌 Key Lease Info")
    st.code(extracted_info)

    with st.spinner("🔧 Generating workflow..."):
        workflow = generate_workflow(extracted_info)
    st.subheader("🛠️ Recommended Workflow")
    st.code(workflow)

    st.subheader("🔄 Workflow Diagram")
    render_workflow(workflow)

    with st.spinner("📈 Estimating value..."):
        value = estimate_value(extracted_info, workflow)
    st.subheader("💡 Value Unlocked")
    st.success(value)
