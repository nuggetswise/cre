#!/bin/bash
echo "🔧 Rebuilding venv with pinned LLM agent stack..."

deactivate 2>/dev/null
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install streamlit==1.33.0 \
    crewai==0.10.0 \
    langchain==0.1.13 \
    langchain-core==0.1.42 \
    langsmith==0.0.93 \
    pydantic==1.10.13 \
    cohere==5.15.0 \
    openai==1.38.0 \
    google-generativeai==0.3.2 \
    groq==0.5.0 \
    graphviz \
    python-dotenv \
    pymupdf

echo "✅ Venv ready. Run: streamlit run app.py"