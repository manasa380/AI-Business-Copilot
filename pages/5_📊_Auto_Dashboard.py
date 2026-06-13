import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import require_login, get_user

# -----------------------
# AUTH CHECK (FIXED)
# -----------------------
require_login()

user = get_user()

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Auto Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------
# SIDEBAR USER INFO
# -----------------------
with st.sidebar:
    st.success(f"👤 {user.name}")
    st.info(f"📧 {user.email}")

# -----------------------
# DATA CHECK
# -----------------------
df = st.session_state.get("df")

if df is None or not isinstance(df, pd.DataFrame) or df.empty:
    st.warning("⚠️ Upload dataset first")
    st.stop()

# -----------------------
# COLUMN DETECTION
# -----------------------
numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(include="object").columns.tolist()

# -----------------------
# TITLE
# -----------------------
st.title("📊 AI Auto Dashboard Builder")
st.caption("Smart automated analytics for your business data")

# -----------------------
# KPI SECTION
# -----------------------
st.subheader("📌 KPI Overview")

memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024

c1, c2, c3, c4 = st.columns(4)

c1.metric("Rows", f"{len(df):,}")
c2.metric("Columns", len(df.columns))
c3.metric("Numeric Features", len(numeric_cols))
c4.metric("Memory (MB)", f"{memory_mb:.2f}")

st.divider()

# -----------------------
# NUMERIC ANALYTICS
# -----------------------
if numeric_cols:
    st.subheader("📈 Numeric Analysis")

    for col in numeric_cols[:3]:

        c1, c2 = st.columns(2)

        with c1:
            st.plotly_chart(
                px.line(df, y=col, title=f"{col} Trend"),
                width='stretch'
            )

        with c2:
            st.plotly_chart(
                px.histogram(df, x=col, title=f"{col} Distribution"),
                width='stretch'
            )

# -----------------------
# CATEGORICAL ANALYSIS
# -----------------------
if categorical_cols:
    st.subheader("📊 Categorical Insights")

    for col in categorical_cols[:2]:

        top_values = df[col].value_counts().nlargest(8).reset_index()
        top_values.columns = [col, "count"]

        st.plotly_chart(
            px.pie(top_values, names=col, values="count", title=f"{col} Distribution"),
            width='stretch'
        )

# -----------------------
# CORRELATION ANALYSIS
# -----------------------
if len(numeric_cols) > 1:
    st.subheader("🔥 Correlation Analysis")

    corr = df[numeric_cols].corr()

    st.plotly_chart(
        px.imshow(corr, text_auto=True, title="Feature Correlation Heatmap"),
        width='stretch'
    )

# -----------------------
# AI INSIGHTS
# -----------------------
st.subheader("🤖 Auto AI Insights")

if numeric_cols:
    col = numeric_cols[0]

    st.info(f"""
🔹 Primary Metric: {col}

🔹 Mean: {df[col].mean():.2f}

🔹 Max: {df[col].max():.2f}

🔹 Min: {df[col].min():.2f}

🔹 Missing Values: {df[col].isna().sum()}
""")

# -----------------------
# RAW DATA
# -----------------------
with st.expander("📂 View Dataset"):
    st.dataframe(df, width='stretch')