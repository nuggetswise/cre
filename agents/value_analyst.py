from crewai import Agent
from langchain.llms import OpenAI, Cohere
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LLM based on available API keys
api_key_openai = os.getenv("OPENAI_API_KEY")
api_key_cohere = os.getenv("COHERE_API_KEY")
api_key_gemini = os.getenv("GEMINI_API_KEY")

# Choose LLM provider with fallback options
if api_key_openai:
    llm = OpenAI(api_key=api_key_openai, temperature=0.2)
elif api_key_cohere:
    llm = Cohere(api_key=api_key_cohere, temperature=0.2)
elif api_key_gemini:
    from langchain.llms import GooglePalm
    llm = GooglePalm(api_key=api_key_gemini, temperature=0.2)
else:
    raise ValueError("No API key found for any supported LLM provider")

value_analyst = Agent(
    role="Value Analyst",
    goal="Summarize value delivered by automating the lease workflow",
    backstory="You focus on ROI, cost savings, and value articulation for AI transformations.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)
