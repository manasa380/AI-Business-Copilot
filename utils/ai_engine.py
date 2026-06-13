import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)


def analyze_data(df, question):

    sample = df.head(20).to_string()

    prompt = f"""
You are an advanced AI Business Copilot.

Dataset:
{sample}

User Question:
{question}

Provide:
- Insights
- Trends
- KPIs
- Risks
- Opportunities
- Business recommendation

Be clear and professional.
"""

    try:
        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Error: {str(e)}"


def normal_chat(question):

    prompt = f"""
You are an advanced AI assistant like ChatGPT.

Question:
{question}

Answer clearly and professionally.
"""

    try:
        response = llm.invoke(prompt)
        return response.content

    except Exception as e:
        return f"Error: {str(e)}"