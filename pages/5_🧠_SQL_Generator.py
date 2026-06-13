import streamlit as st
import pandas as pd
import sqlite3
from utils.ai_engine import llm
from utils.auth import require_login, get_user

# -------------------------
# AUTH CHECK (FIXED)
# -------------------------
require_login()

user = get_user()

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="AI SQL Generator",
    page_icon="🧠",
    layout="wide"
)

# -------------------------
# SIDEBAR USER INFO
# -------------------------
with st.sidebar:
    st.success(f"👤 {user.name}")
    st.info(f"📧 {user.email}")

# -------------------------
# DATA CHECK
# -------------------------
df = st.session_state.get("df")

if df is None or not isinstance(df, pd.DataFrame) or df.empty:
    st.warning("⚠️ Upload dataset first")
    st.stop()

# -------------------------
# TITLE
# -------------------------
st.title("🧠 AI SQL Generator Pro")
st.caption("Natural Language → SQL → Insights Engine")

st.subheader("📊 Dataset Preview")
st.dataframe(df.head(), width='stretch')

# -------------------------
# COLUMN INFO
# -------------------------
columns_info = "\n".join(
    [f"- {col} ({df[col].dtype})" for col in df.columns]
)

st.code(columns_info)

# -------------------------
# INPUT
# -------------------------
question = st.text_area(
    "Ask your SQL question",
    placeholder="e.g. total sales by region, top 10 customers"
)

# -------------------------
# HELPERS
# -------------------------
def clean_sql(sql: str) -> str:
    return str(sql).replace("```sql", "").replace("```", "").strip()

def is_safe_sql(sql: str) -> bool:
    blocked = ["drop", "delete", "update", "insert", "alter", "truncate"]
    return not any(word in sql.lower() for word in blocked)

def run_sql(df, query):
    conn = sqlite3.connect(":memory:")
    df.to_sql("business_data", conn, index=False, if_exists="replace")
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

# -------------------------
# GENERATE SQL
# -------------------------
if st.button("🚀 Generate SQL"):

    if not question.strip():
        st.warning("Please enter a question")
        st.stop()

    prompt = f"""
You are a senior SQL expert.

RULES:
- Return ONLY SQLite SQL
- Table: business_data
- Always use GROUP BY for aggregations
- Use COUNT(DISTINCT ...) when needed
- Always ORDER BY DESC for ranking
- LIMIT 10 for top results
- Avoid duplicate rows
- NO explanations

COLUMNS:
{columns_info}

QUESTION:
{question}
"""

    try:
        response = llm.invoke(prompt)
        sql_query = clean_sql(getattr(response, "content", str(response)))

        st.subheader("🧾 Generated SQL")
        st.code(sql_query, language="sql")

        # -------------------------
        # SECURITY CHECK
        # -------------------------
        if not is_safe_sql(sql_query):
            st.error("❌ Unsafe SQL detected")
            st.stop()

        # -------------------------
        # EXECUTE SQL
        # -------------------------
        st.subheader("📊 Result")

        try:
            result_df = run_sql(df, sql_query)

            result_df = result_df.drop_duplicates().reset_index(drop=True)

            st.dataframe(result_df, width='stretch')

        except Exception as e:
            st.error(f"SQL Execution Error: {str(e)}")

    except Exception as e:
        st.error(f"LLM Error: {str(e)}")

# -------------------------
# EXAMPLES
# -------------------------
st.divider()

st.subheader("💡 Example Questions")

st.markdown("""
- Count of regions  
- Total sales by category  
- Average profit by region  
- Top 10 customers by revenue  
- Monthly sales trend  
""")