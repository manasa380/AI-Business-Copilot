import streamlit as st
import pandas as pd
import plotly.express as px
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
    page_title="AI Insights Engine",
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
# COLUMN DETECTION
# -------------------------
numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(include="object").columns.tolist()

# -------------------------
# TITLE
# -------------------------
st.title("🧠 AI Insights Engine (Pro)")

# -------------------------
# KPI DASHBOARD
# -------------------------
st.subheader("📊 Dataset Health Overview")

missing_total = int(df.isnull().sum().sum())
duplicate_total = int(df.duplicated().sum())
memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024

c1, c2, c3, c4 = st.columns(4)

c1.metric("Rows", f"{len(df):,}")
c2.metric("Columns", len(df.columns))
c3.metric("Missing Values", missing_total)
c4.metric("Memory (MB)", f"{memory_mb:.2f}")