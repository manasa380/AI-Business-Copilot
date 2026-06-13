import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from utils.auth import require_login, get_user

# ----------------------------
# AUTH CHECK (FIXED)
# ----------------------------
require_login()

user = get_user()

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Upload Data",
    page_icon="📂",
    layout="wide"
)

# ----------------------------
# HEADER
# ----------------------------
st.title("📂 Data Upload Center")
st.caption("Upload your dataset to unlock AI analytics, forecasting & insights")

with st.sidebar:
    st.success(f"👤 {user.name}")
    st.info(f"📧 {user.email}")

# ----------------------------
# FILE UPLOAD
# ----------------------------
uploaded_file = st.file_uploader(
    "Upload your dataset",
    type=["csv", "xlsx"],
    help="Supported formats: CSV, Excel (xlsx)"
)

# ----------------------------
# PROCESS FILE
# ----------------------------
if uploaded_file:

    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > 50:
        st.error("❌ File too large. Please upload under 50MB.")
        st.stop()

    try:
        df = load_data(uploaded_file)

        if df.empty:
            st.error("❌ Dataset is empty")
            st.stop()

        # Save dataset globally
        st.session_state["df"] = df

        st.success("✅ Dataset uploaded successfully!")

        # ----------------------------
        # KPI SECTION
        # ----------------------------
        st.subheader("📊 Dataset Overview")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Rows", f"{len(df):,}")
        c2.metric("Columns", len(df.columns))
        c3.metric("Missing Values", int(df.isnull().sum().sum()))

        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        c4.metric("Memory (MB)", f"{memory_mb:.2f}")

        st.divider()

        # ----------------------------
        # DATA PREVIEW
        # ----------------------------
        with st.expander("👀 Preview Data (Top 100 rows)", expanded=True):
            st.dataframe(df.head(100), width='stretch')

        # ----------------------------
        # COLUMN INFO
        # ----------------------------
        with st.expander("📋 Column Information"):
            info_df = pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.astype(str)
            })
            st.dataframe(info_df, width='stretch')

        # ----------------------------
        # DATA QUALITY
        # ----------------------------
        with st.expander("🔍 Data Quality Report"):
            quality_df = pd.DataFrame({
                "Column": df.columns,
                "Missing Values": df.isnull().sum().values
            })
            st.dataframe(quality_df, width='stretch')

        # ----------------------------
        # SUCCESS FOOTER
        # ----------------------------
        st.success(
            "🚀 Ready for Dashboard • AI Insights • Forecasting • SQL Generator • AutoML"
        )

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")