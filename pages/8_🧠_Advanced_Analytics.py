import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils.auth import require_login, get_user

# ------------------------
# AUTH CHECK (FIXED)
# ------------------------
require_login()

user = get_user()

# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(
    page_title="Advanced Analytics Engine",
    page_icon="🧠",
    layout="wide"
)

# ------------------------
# SIDEBAR USER INFO
# ------------------------
with st.sidebar:
    st.success(f"👤 {user.name}")
    st.info(f"📧 {user.email}")

# ------------------------
# TITLE
# ------------------------
st.title("🧠 Advanced Analytics Engine (Pro)")
st.caption("Deep Data Profiling + Statistical Intelligence Layer")

# ------------------------
# DATA CHECK
# ------------------------
df = st.session_state.get("df")

if df is None or not isinstance(df, pd.DataFrame) or df.empty:
    st.warning("⚠️ Upload dataset first")
    st.stop()

# ------------------------
# COLUMN DETECTION
# ------------------------
numeric_cols = df.select_dtypes(include="number").columns.tolist()
categorical_cols = df.select_dtypes(include="object").columns.tolist()

# ------------------------
# DATA QUALITY METRICS
# ------------------------
st.subheader("📊 Data Quality Overview")

missing = df.isnull().sum().sum()
duplicates = df.duplicated().sum()
memory = df.memory_usage(deep=True).sum() / 1024 / 1024

c1, c2, c3, c4 = st.columns(4)

c1.metric("Rows", len(df))
c2.metric("Columns", len(df.columns))
c3.metric("Missing", int(missing))
c4.metric("Duplicates", int(duplicates))

st.info(f"💾 Memory Usage: {memory:.2f} MB")

st.divider()

# ------------------------
# CORRELATION MATRIX
# ------------------------
if len(numeric_cols) > 1:
    st.subheader("🔥 Correlation Intelligence Map")

    corr = df[numeric_cols].corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu",
        title="Feature Correlation Matrix"
    )

    st.plotly_chart(fig, width='stretch')
else:
    st.warning("Need at least 2 numeric columns")

# ------------------------
# OUTLIER DETECTION
# ------------------------
if numeric_cols:
    st.subheader("📉 Outlier Detection Engine")

    col = st.selectbox("Select Column", numeric_cols)

    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = df[(df[col] < lower) | (df[col] > upper)]

    c1, c2 = st.columns(2)
    c1.metric("Outliers", len(outliers))
    c2.metric("Outlier %", f"{(len(outliers)/len(df))*100:.2f}%")

    st.plotly_chart(px.box(df, y=col, title=f"Outlier Distribution - {col}"),
                    width='stretch')

# ------------------------
# DISTRIBUTION ANALYSIS
# ------------------------
if numeric_cols:
    st.subheader("📊 Distribution Intelligence")

    col2 = st.selectbox("Select Column", numeric_cols, key="dist_col")

    st.plotly_chart(
        px.histogram(df, x=col2, nbins=30, marginal="box",
                     title=f"Distribution Analysis - {col2}"),
        width='stretch'
    )

# ------------------------
# DATA QUALITY SCORE
# ------------------------
st.subheader("💡 Data Quality Insights Engine")

quality_score = 100 - ((missing / (len(df)*len(df.columns))) * 100)

if missing > 0:
    st.warning(f"⚠ Missing values detected: {missing}")

if duplicates > 0:
    st.warning(f"⚠ Duplicate rows detected: {duplicates}")

st.metric("Dataset Quality Score", f"{quality_score:.2f}/100")

# ------------------------
# AI INSIGHTS ENGINE
# ------------------------
st.subheader("🤖 Smart AI Insights Engine")

if numeric_cols:
    insights = []

    for col in numeric_cols[:3]:

        mean = df[col].mean()
        std = df[col].std()
        skew = df[col].skew()

        if abs(skew) > 1:
            pattern = "Highly Skewed"
        elif std > mean:
            pattern = "High Volatility"
        else:
            pattern = "Normal Distribution"

        insights.append({
            "Metric": col,
            "Mean": round(mean, 2),
            "Std Dev": round(std, 2),
            "Skewness": round(skew, 2),
            "Pattern": pattern
        })

    st.dataframe(pd.DataFrame(insights), width='stretch')

    top = numeric_cols[0]

    st.success(f"""
🔹 Primary Metric: {top}

🔹 Average: {df[top].mean():.2f}

🔹 Volatility: {df[top].std():.2f}

🔹 Insight: {"High instability detected" if df[top].std() > df[top].mean() else "Stable dataset"}
""")

# ------------------------
# RAW DATA
# ------------------------
with st.expander("📂 View Dataset"):
    st.dataframe(df, width='stretch')