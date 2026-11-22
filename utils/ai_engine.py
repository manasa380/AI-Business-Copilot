
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load local environment variables
load_dotenv()


# -----------------------------------------
# 1. GET GROQ API KEY
# -----------------------------------------

def get_api_key():
    """Get API key from Streamlit Secrets or local .env."""

    api_key = None

    # Streamlit Cloud Secrets
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = None

    # Local environment fallback
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return str(api_key).strip()


# -----------------------------------------
# 2. CREATE GROQ MODEL
# -----------------------------------------

def _create_llm():
    """Initialize Groq LLM."""

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Add it in Streamlit Cloud Secrets "
            "or your local .env file."
        )

    return ChatGroq(
        groq_api_key=api_key,
        model="openai/gpt-oss-120b",
        temperature=0.3
    )


# -----------------------------------------
# 3. LAZY MODEL INITIALIZATION
# -----------------------------------------

_llm = None


def get_llm():
    """Return cached Groq model."""

    global _llm

    if _llm is None:
        _llm = _create_llm()

    return _llm


# Backward compatibility for existing imports
# from utils.ai_engine import llm

class LazyLLM:

    def __getattr__(self, name):
        return getattr(get_llm(), name)

    def invoke(self, *args, **kwargs):
        return get_llm().invoke(*args, **kwargs)


llm = LazyLLM()


# -----------------------------------------
# 4. DATASET ANALYSIS
# -----------------------------------------

def analyze_data(df, prompt):
    """
    Analyze uploaded dataframe using Groq.

    Usage:
    response = analyze_data(df, user_prompt)
    """

    try:

        if df is None:
            return "Please upload a dataset first."

        if df.empty:
            return "The uploaded dataset is empty."

        dataset_info = f"""
DATASET OVERVIEW

Total Rows: {df.shape[0]}
Total Columns: {df.shape[1]}

Column Names:
{', '.join(map(str, df.columns))}

Data Types:
{df.dtypes.to_string()}

Sample Records:
{df.head(5).to_string(index=False)}

Basic Statistics:
{df.describe(include='all').to_string()}
"""

        full_prompt = f"""
You are an expert AI Business Data Analyst.

Analyze the uploaded business dataset.

DATASET INFORMATION:
{dataset_info}

USER QUESTION:
{prompt}

Provide your answer using these sections:

1. Executive Summary
2. Important Data Insights
3. Business Trends and Patterns
4. Potential Problems and Risks
5. Business Opportunities
6. Actionable Recommendations

Use simple, clear and professional business language.

Only make conclusions supported by the available dataset.
"""

        response = get_llm().invoke(full_prompt)

        if hasattr(response, "content"):
            return response.content

        return str(response)

    except Exception as e:
        return f"AI Analysis Error: {str(e)}"


# -----------------------------------------
# 5. GENERAL AI RESPONSE
# -----------------------------------------

def generate_response(prompt):
    """Generate a general AI response."""

    try:

        response = get_llm().invoke(prompt)

        if hasattr(response, "content"):
            return response.content

        return str(response)

    except Exception as e:
        return f"AI Response Error: {str(e)}"


# -----------------------------------------
# 6. AI EXECUTIVE SUMMARY
# -----------------------------------------

def generate_executive_summary(df):
    """Generate AI-powered business executive summary."""

    prompt = """
    Generate a professional executive summary
    based on the uploaded business dataset.

    Include:

    1. Overall business performance
    2. Key findings
    3. Important trends
    4. Business risks
    5. Growth opportunities
    6. Actionable recommendations

    Keep the summary clear, concise and useful.
    """

    return analyze_data(df, prompt)
