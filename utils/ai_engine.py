
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_api_key():
    """Get Groq API key from Streamlit Cloud or local environment."""

    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    return api_key.strip() if api_key else None


def _create_llm():
    """Create Groq model only when required."""

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Add it in Streamlit Cloud Secrets or your local .env file."
        )

    return ChatGroq(
        groq_api_key=api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.3
    )


_llm = None


def get_llm():
    """Return cached Groq model."""

    global _llm

    if _llm is None:
        _llm = _create_llm()

    return _llm


class LazyLLM:
    """Preserve compatibility with existing imports: from utils.ai_engine import llm"""

    def __getattr__(self, name):
        return getattr(get_llm(), name)

    def invoke(self, *args, **kwargs):
        return get_llm().invoke(*args, **kwargs)


# Backward-compatible lazy model
llm = LazyLLM()


def analyze_data(df, prompt):
    """
    Analyze uploaded dataframe using Groq.

    Compatible with:
    response = analyze_data(df, user_prompt)
    """

    try:
        if df is None or df.empty:
            return "No dataset available. Please upload a dataset first."

        dataset_info = f"""
Rows: {df.shape[0]}
Columns: {df.shape[1]}

Column Names:
{', '.join(map(str, df.columns))}

Sample Data:
{df.head(5).to_string(index=False)}
"""

        full_prompt = f"""
You are an expert business data analyst.

Analyze the following business dataset.

Dataset Information:
{dataset_info}

User Question:
{prompt}

Provide:
1. Key insights
2. Important patterns
3. Business opportunities
4. Actionable recommendations

Use simple language and explain findings clearly.
"""

        response = get_llm().invoke(full_prompt)

        return (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

    except Exception as e:
        return f"AI Analysis Error: {str(e)}"
