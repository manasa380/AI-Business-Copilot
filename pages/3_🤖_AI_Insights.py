import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.auth import require_login, get_user
from utils.ai_engine import llm

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="AI Insights Engine",
    page_icon="🧠",
    layout="wide"
)

# -------------------------
# AUTH CHECK
# -------------------------
try:
    require_login()
    user = get_user()
except Exception:
    user = None

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:

    if user:

        st.success(
            f"👤 {getattr(user,'name','User')}"
        )

        st.info(
            f"📧 {getattr(user,'email','Unknown')}"
        )

# -------------------------
# DATA CHECK
# -------------------------
df = st.session_state.get("df")

if df is None:
    st.warning(
        "⚠️ Upload dataset first"
    )
    st.stop()

if not isinstance(df, pd.DataFrame):
    st.error(
        "Invalid dataframe"
    )
    st.stop()

if df.empty:
    st.error(
        "Dataset is empty"
    )
    st.stop()

# -------------------------
# COLUMN DETECTION
# -------------------------
numeric_cols = (
    df.select_dtypes(
        include="number"
    )
    .columns
    .tolist()
)

categorical_cols = (
    df.select_dtypes(
        include="object"
    )
    .columns
    .tolist()
)

# -------------------------
# TITLE
# -------------------------
st.title(
    "🧠 AI Insights Engine Pro"
)

# -------------------------
# KPI OVERVIEW
# -------------------------
st.subheader(
    "📊 Dataset Health Overview"
)

missing_total = int(
    df.isnull().sum().sum()
)

duplicate_total = int(
    df.duplicated().sum()
)

memory_mb = round(
    df.memory_usage(deep=True)
    .sum()
    / 1024
    / 1024,
    2
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Rows",
    f"{len(df):,}"
)

c2.metric(
    "Columns",
    len(df.columns)
)

c3.metric(
    "Missing Values",
    missing_total
)

c4.metric(
    "Memory MB",
    memory_mb
)

# -------------------------
# DATA QUALITY SCORE
# -------------------------
st.subheader(
    "🎯 Dataset Quality Score"
)

total_cells = (
    df.shape[0]
    * df.shape[1]
)

if total_cells > 0:

    missing_pct = (
        missing_total
        / total_cells
    ) * 100

else:
    missing_pct = 0

quality_score = max(
    0,
    100 - missing_pct
)

st.progress(
    quality_score / 100
)

st.success(
    f"Quality Score: "
    f"{quality_score:.1f}%"
)

# -------------------------
# CORRELATION ANALYSIS
# -------------------------
if len(numeric_cols) > 1:

    st.subheader(
        "🔥 Correlation Analysis"
    )

    try:

        corr = (
            df[numeric_cols]
            .corr()
        )

        fig = go.Figure(
            data=go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.columns
            )
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    except Exception as e:

        st.error(
            f"Correlation Error: {e}"
        )

# -------------------------
# ANOMALY DETECTION
# -------------------------
if len(numeric_cols) > 0:

    st.subheader(
        "🚨 Anomaly Detection"
    )

    anomaly_col = st.selectbox(
        "Select Column",
        numeric_cols,
        key="anomaly"
    )

    try:

        Q1 = (
            df[anomaly_col]
            .quantile(0.25)
        )

        Q3 = (
            df[anomaly_col]
            .quantile(0.75)
        )

        IQR = Q3 - Q1

        anomalies = df[
            (
                df[anomaly_col]
                < Q1 - 1.5 * IQR
            )
            |
            (
                df[anomaly_col]
                > Q3 + 1.5 * IQR
            )
        ]

        st.metric(
            "Outliers",
            len(anomalies)
        )

        with st.expander(
            "View Outliers"
        ):
            st.dataframe(
                anomalies,
                width="stretch"
            )

    except Exception as e:

        st.error(
            f"Anomaly Error: {e}"
        )

# -------------------------
# TREND ANALYSIS
# -------------------------
if len(numeric_cols) > 0:

    st.subheader(
        "📈 Trend Analysis"
    )

    trend_col = st.selectbox(
        "Select Metric",
        numeric_cols,
        key="trend"
    )

    try:

        fig = px.line(
            df,
            y=trend_col,
            title=f"{trend_col} Trend"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    except Exception as e:

        st.error(
            f"Trend Error: {e}"
        )

# -------------------------
# DISTRIBUTION
# -------------------------
if len(numeric_cols) > 0:

    st.subheader(
        "📊 Distribution Analysis"
    )

    dist_col = st.selectbox(
        "Select Distribution",
        numeric_cols,
        key="dist"
    )

    try:

        fig = px.histogram(
            df,
            x=dist_col,
            nbins=30
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    except Exception as e:

        st.error(
            f"Distribution Error: {e}"
        )

# -------------------------
# CATEGORY ANALYSIS
# -------------------------
if len(categorical_cols) > 0:

    st.subheader(
        "🏷 Category Analysis"
    )

    cat_col = st.selectbox(
        "Select Category",
        categorical_cols,
        key="cat"
    )

    try:

        fig = px.pie(
            df,
            names=cat_col
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    except Exception as e:

        st.error(
            f"Category Error: {e}"
        )

# -------------------------
# SMART RECOMMENDATIONS
# -------------------------
st.subheader(
    "💡 Smart Recommendations"
)

recommendations = []

if missing_total > 0:
    recommendations.append(
        "Clean missing values."
    )

if duplicate_total > 0:
    recommendations.append(
        "Remove duplicate records."
    )

if len(numeric_cols) > 5:
    recommendations.append(
        "Feature selection may improve performance."
    )

if len(df) > 10000:
    recommendations.append(
        "Dataset is suitable for forecasting."
    )

if not recommendations:
    recommendations.append(
        "Dataset appears healthy."
    )

for rec in recommendations:
    st.success(rec)

# -------------------------
# AI SUMMARY
# -------------------------
st.subheader(
    "🤖 AI Executive Summary"
)

if st.button(
    "Generate AI Summary"
):

    try:

        with st.spinner(
            "Generating..."
        ):

            prompt = f"""
Analyze this dataset.

Rows: {len(df)}
Columns: {len(df.columns)}
Missing Values: {missing_total}
Duplicate Rows: {duplicate_total}

Summary:
{df.describe().to_string()}

Provide:
1. Key Findings
2. Risks
3. Opportunities
4. Recommendations
5. Executive Summary
"""

            result = llm.invoke(
                prompt
            )

            if hasattr(
                result,
                "content"
            ):
                response = result.content
            else:
                response = str(result)

            st.markdown(
                response
            )

    except Exception as e:

        st.error(
            f"AI Error: {e}"
        )

# -------------------------
# DATA PREVIEW
# -------------------------
with st.expander(
    "📂 View Dataset"
):

    st.dataframe(
        
        df,
        width="stretch"
    )