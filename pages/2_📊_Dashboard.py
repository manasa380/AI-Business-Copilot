import streamlit as st
import plotly.express as px
import pandas as pd
from utils.auth import require_login, get_user

# ---------------------------------
# AUTH CHECK (FIXED)
# ---------------------------------
require_login()

user = get_user()

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="AI Business Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------
# USER INFO
# ---------------------------------
with st.sidebar:
    st.success(f"👤 {user.name}")
    st.info(f"📧 {user.email}")

# ---------------------------------
# DATA CHECK
# ---------------------------------
df = st.session_state.get("df")

if df is None or not isinstance(df, pd.DataFrame) or df.empty:
    st.warning("⚠️ Upload dataset first")
    st.stop()

data = df.copy()

numeric_cols = data.select_dtypes(include="number").columns.tolist()
categorical_cols = data.select_dtypes(include="object").columns.tolist()

# ---------------------------------
# FILTERS
# ---------------------------------
st.sidebar.subheader("🎯 Filters")

if categorical_cols:
    filter_col = st.sidebar.selectbox("Filter Column", categorical_cols)

    values = st.sidebar.multiselect(
        "Select Values",
        data[filter_col].dropna().unique()
    )

    if values:
        data = data[data[filter_col].isin(values)]

# ---------------------------------
# TITLE
# ---------------------------------
st.title("📊 AI Business Dashboard")
st.caption("Interactive analytics powered by AI Copilot")

# ---------------------------------
# KPI SECTION
# ---------------------------------
st.subheader("📌 KPI Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Rows", f"{len(data):,}")
c2.metric("Columns", len(data.columns))
c3.metric("Missing Values", int(data.isnull().sum().sum()))

memory = data.memory_usage(deep=True).sum() / 1024 / 1024
c4.metric("Memory (MB)", f"{memory:.2f}")

# ---------------------------------
# NUMERIC KPI
# ---------------------------------
if numeric_cols:
    col = numeric_cols[0]

    st.subheader("📊 Key Metric Insight")

    c5, c6, c7, c8 = st.columns(4)

    c5.metric("Total", round(data[col].sum(), 2))
    c6.metric("Average", round(data[col].mean(), 2))
    c7.metric("Maximum", round(data[col].max(), 2))
    c8.metric("Minimum", round(data[col].min(), 2))

st.divider()

# ---------------------------------
# VISUAL ANALYTICS
# ---------------------------------
st.subheader("📈 Visual Analytics")

if numeric_cols:
    selected_num = st.selectbox("Select Metric", numeric_cols)

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.line(data, y=selected_num, title=f"{selected_num} Trend")
        st.plotly_chart(fig1, width='stretch')

    with col2:
        fig2 = px.histogram(data, x=selected_num, title=f"{selected_num} Distribution")
        st.plotly_chart(fig2, width='stretch')

# ---------------------------------
# CATEGORY ANALYSIS
# ---------------------------------
if categorical_cols:
    st.subheader("🏆 Category Analysis")

    cat_col = st.selectbox("Category Column", categorical_cols)

    top = data[cat_col].value_counts().head(10).reset_index()
    top.columns = [cat_col, "Count"]

    col1, col2 = st.columns(2)

    with col1:
        fig3 = px.bar(top, x=cat_col, y="Count", title="Top Categories")
        st.plotly_chart(fig3, width='stretch')

    with col2:
        fig4 = px.pie(top, names=cat_col, values="Count", title="Distribution")
        st.plotly_chart(fig4, width='stretch')

# ---------------------------------
# CORRELATION
# ---------------------------------
if len(numeric_cols) >= 2:
    st.subheader("🔥 Correlation Analysis")

    corr = data[numeric_cols].corr()
    fig = px.imshow(corr, text_auto=True, title="Correlation Matrix")

    st.plotly_chart(fig, width='stretch')

# ---------------------------------
# DATA QUALITY
# ---------------------------------
st.subheader("🧹 Data Quality")

quality_df = pd.DataFrame({
    "Column": data.columns,
    "Missing Values": data.isnull().sum().values
})

st.dataframe(quality_df, width='stretch')

# ---------------------------------
# RAW DATA
# ---------------------------------
with st.expander("📂 View Dataset"):
    st.dataframe(data, width='stretch')