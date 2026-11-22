
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils.auth import require_login, get_user

# ------------------------
# PAGE CONFIG
# ------------------------
st.set_page_config(
    page_title="Advanced Analytics Engine",
    page_icon="🧠",
    layout="wide"
)

# ------------------------
# AUTH CHECK
# ------------------------
require_login()
user = get_user()

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

# Work on a copy so the shared uploaded dataframe is not modified
df = df.copy()

# ------------------------
# NUMERIC COLUMN DETECTION
# ------------------------
for col in df.columns:

    if pd.api.types.is_numeric_dtype(df[col]):
        continue

    cleaned = (
        df[col]
        .astype("string")
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace(r"^[₹$€£]\s*", "", regex=True)
    )

    converted = pd.to_numeric(cleaned, errors="coerce")

    # Convert only when the column contains actual numeric values
    if converted.notna().any():
        df[col] = converted

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

categorical_cols = df.select_dtypes(
    include=["object", "string", "category"]
).columns.tolist()

# Remove columns with no usable numeric data
numeric_cols = [
    col for col in numeric_cols
    if df[col].notna().any()
]

st.success(f"✅ Detected {len(numeric_cols)} numeric columns")

with st.expander("🔍 Detected Column Types"):
    st.write("Numeric Columns:", numeric_cols)
    st.write("Categorical Columns:", categorical_cols)
    st.dataframe(
        pd.DataFrame({
            "Column": df.columns,
            "Data Type": [str(dtype) for dtype in df.dtypes]
        }),
        width="stretch"
    )

# ------------------------
# DATA QUALITY METRICS
# ------------------------
st.subheader("📊 Data Quality Overview")

missing = int(df.isnull().sum().sum())
duplicates = int(df.duplicated().sum())
memory = df.memory_usage(deep=True).sum() / 1024 / 1024

c1, c2, c3, c4 = st.columns(4)

c1.metric("Rows", len(df))
c2.metric("Columns", len(df.columns))
c3.metric("Missing", missing)
c4.metric("Duplicates", duplicates)

st.info(f"💾 Memory Usage: {memory:.2f} MB")

st.divider()

# ------------------------
# CORRELATION MATRIX
# ------------------------
st.subheader("🔥 Correlation Intelligence Map")

if len(numeric_cols) >= 2:

    corr = df[numeric_cols].corr()

    if corr.notna().values.any():

        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale="RdBu",
            title="Feature Correlation Matrix",
            aspect="auto"
        )

        st.plotly_chart(fig, width="stretch")

    else:
        st.info("Not enough variation in numeric columns to calculate correlation.")

else:
    st.warning(
        "Need at least 2 numeric columns. "
        "Your dataset currently has fewer than 2 detected numeric columns."
    )

# ------------------------
# OUTLIER DETECTION
# ------------------------
st.subheader("📉 Outlier Detection Engine")

if numeric_cols:

    col = st.selectbox(
        "Select Column",
        numeric_cols,
        key="outlier_col"
    )

    values = df[col].dropna()

    if len(values) >= 2:

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = values[(values < lower) | (values > upper)]

        c1, c2 = st.columns(2)

        c1.metric("Outliers", len(outliers))
        c2.metric(
            "Outlier %",
            f"{(len(outliers) / len(values)) * 100:.2f}%"
        )

        st.plotly_chart(
            px.box(
                values,
                title=f"Outlier Distribution - {col}"
            ),
            width="stretch"
        )

    else:
        st.info("Not enough valid values for outlier detection.")

else:
    st.info("No numeric columns available for outlier detection.")

# ------------------------
# DISTRIBUTION ANALYSIS
# ------------------------
st.subheader("📊 Distribution Intelligence")

if numeric_cols:

    col2 = st.selectbox(
        "Select Column",
        numeric_cols,
        key="dist_col"
    )

    if df[col2].notna().sum() > 0:

        st.plotly_chart(
            px.histogram(
                df,
                x=col2,
                nbins=30,
                marginal="box",
                title=f"Distribution Analysis - {col2}"
            ),
            width="stretch"
        )

else:
    st.info("No numeric columns available for distribution analysis.")

# ------------------------
# DATA QUALITY SCORE
# ------------------------
st.subheader("💡 Data Quality Insights Engine")

total_cells = len(df) * len(df.columns)

quality_score = (
    100 - (missing / total_cells * 100)
    if total_cells > 0 else 0
)

if missing > 0:
    st.warning(f"⚠️ Missing values detected: {missing}")

if duplicates > 0:
    st.warning(f"⚠️ Duplicate rows detected: {duplicates}")

st.metric(
    "Dataset Quality Score",
    f"{quality_score:.2f}/100"
)

# ------------------------
# AI INSIGHTS ENGINE
# ------------------------
st.subheader("🤖 Smart AI Insights Engine")

if numeric_cols:

    insights = []

    for col in numeric_cols[:3]:

        values = df[col].dropna()

        if values.empty:
            continue

        mean = values.mean()
        std = values.std()
        skew = values.skew()

        if pd.isna(skew):
            pattern = "Insufficient variation"
        elif abs(skew) > 1:
            pattern = "Highly Skewed"
        elif pd.notna(std) and std > abs(mean):
            pattern = "High Volatility"
        else:
            pattern = "Relatively Stable"

        insights.append({
            "Metric": col,
            "Mean": round(mean, 2),
            "Std Dev": round(std, 2) if pd.notna(std) else 0,
            "Skewness": round(skew, 2) if pd.notna(skew) else 0,
            "Pattern": pattern
        })

    if insights:

        st.dataframe(
            pd.DataFrame(insights),
            width="stretch"
        )

        top = numeric_cols[0]
        values = df[top].dropna()

        mean = values.mean()
        std = values.std()

        st.success(f"""
🔹 Primary Metric: {top}

🔹 Average: {mean:.2f}

🔹 Volatility: {std:.2f if pd.notna(std) else 0}

🔹 Insight: {
    "High instability detected"
    if pd.notna(std) and std > abs(mean)
    else "Relatively stable dataset"
}
""")

else:
    st.info("Upload a dataset containing numeric values to generate insights.")

# ------------------------
# RAW DATA
# ------------------------
with st.expander("📂 View Dataset"):
    st.dataframe(df, width="stretch")
