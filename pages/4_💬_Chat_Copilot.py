import streamlit as st
import pandas as pd
import plotly.express as px
from utils.ai_engine import analyze_data
from utils.auth import require_login, get_user

# -----------------------------
# AUTH CHECK (FIXED)
# -----------------------------
require_login()

user = get_user()

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Copilot",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# SIDEBAR USER INFO
# -----------------------------
with st.sidebar:
    st.success(f"👤 {user.name}")
    st.info(f"📧 {user.email}")

# -----------------------------
# TITLE
# -----------------------------
st.title("🤖 AI Business Copilot Pro")
st.caption("Chat with your dataset using AI-powered insights")

# -----------------------------
# DATA CHECK
# -----------------------------
df = st.session_state.get("df")

if df is None or not isinstance(df, pd.DataFrame) or df.empty:
    st.warning("⚠️ Upload dataset first for AI analysis")
    st.stop()

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None

# -----------------------------
# QUICK ACTIONS
# -----------------------------
st.subheader("⚡ Quick Actions")

c1, c2, c3, c4 = st.columns(4)

if c1.button("📊 Analyze"):
    st.session_state.quick_prompt = "Analyze my dataset"

if c2.button("📈 Trends"):
    st.session_state.quick_prompt = "Find trends in data"

if c3.button("💡 KPIs"):
    st.session_state.quick_prompt = "Suggest important KPIs"

if c4.button("📉 Insights"):
    st.session_state.quick_prompt = "Give business insights"

# -----------------------------
# CHAT INPUT
# -----------------------------
user_prompt = st.chat_input("Ask anything about your data...")

if st.session_state.quick_prompt:
    user_prompt = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

# -----------------------------
# PROCESS CHAT
# -----------------------------
if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.spinner("🤖 AI is thinking..."):
        try:
            response = analyze_data(df, user_prompt)
        except Exception as e:
            response = f"❌ Error: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": response})

# -----------------------------
# CHAT UI
# -----------------------------
st.subheader("💬 Conversation")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div style="background:#1f2937;padding:12px;border-radius:10px;margin:5px 0;color:white">
            👤 <b>You</b><br>{msg['content']}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="background:#0f172a;padding:12px;border-radius:10px;margin:5px 0;border-left:4px solid #38bdf8;color:white">
            🤖 <b>AI</b><br>{msg['content']}
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------
# LIVE ANALYTICS
# -----------------------------
st.divider()
st.subheader("📊 Live Analytics Dashboard")

numeric_cols = df.select_dtypes(include="number").columns.tolist()

if numeric_cols:

    col = st.selectbox("Select KPI Column", numeric_cols)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Average", round(df[col].mean(), 2))
    c2.metric("Max", round(df[col].max(), 2))
    c3.metric("Min", round(df[col].min(), 2))
    c4.metric("Total", round(df[col].sum(), 2))

    st.plotly_chart(px.line(df, y=col, title="Trend Analysis"), width='stretch')
    st.plotly_chart(px.histogram(df, x=col, title="Distribution"), width='stretch')
    st.plotly_chart(px.box(df, y=col, title="Outlier Detection"), width='stretch')

# -----------------------------
# CLEAR CHAT
# -----------------------------
st.divider()

if st.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.rerun()