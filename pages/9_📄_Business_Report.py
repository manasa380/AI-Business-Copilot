import streamlit as st
import pandas as pd
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
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
    page_title="AI Business Report",
    page_icon="📄",
    layout="wide"
)

# -------------------------
# UI HEADER
# -------------------------
st.title("📄 AI Business Intelligence Report")
st.caption("Automated professional analytics report generator")

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

if df is None or df.empty:
    st.warning("Upload dataset first")
    st.stop()

st.subheader("📊 Dataset Preview")
st.dataframe(df.head(), width='stretch')

numeric_cols = df.select_dtypes(include="number").columns.tolist()

# -------------------------
# SAFE STATS FUNCTION
# -------------------------
def safe(col, func):
    try:
        return round(func(df[col]), 2)
    except:
        return "N/A"

# -------------------------
# GENERATE REPORT
# -------------------------
if st.button("🚀 Generate Report"):

    with st.spinner("Generating AI Business Report..."):

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(tmp.name)

        styles = getSampleStyleSheet()

        story = []

        title = styles["Title"]
        h2 = styles["Heading2"]
        body = styles["BodyText"]

        # -------------------------
        # TITLE
        # -------------------------
        story.append(Paragraph("AI BUSINESS INTELLIGENCE REPORT", title))
        story.append(Spacer(1, 15))

        # -------------------------
        # OVERVIEW
        # -------------------------
        story.append(Paragraph("Dataset Overview", h2))
        story.append(Paragraph(f"Rows: {len(df)}", body))
        story.append(Paragraph(f"Columns: {len(df.columns)}", body))
        story.append(Paragraph(f"Missing Values: {int(df.isnull().sum().sum())}", body))
        story.append(Paragraph(f"Duplicates: {int(df.duplicated().sum())}", body))
        story.append(Spacer(1, 10))

        # -------------------------
        # KPI SECTION
        # -------------------------
        story.append(Paragraph("Key Performance Indicators", h2))

        if numeric_cols:
            for col in numeric_cols[:6]:

                story.append(Paragraph(f"<b>{col}</b>", body))

                story.append(Paragraph(
                    f"""
                    Mean: {safe(col, df[col].mean)}<br/>
                    Max: {safe(col, df[col].max)}<br/>
                    Min: {safe(col, df[col].min)}<br/>
                    Std Dev: {safe(col, df[col].std)}
                    """,
                    body
                ))

                story.append(Spacer(1, 8))
        else:
            story.append(Paragraph("No numeric columns found", body))

        # -------------------------
        # DATA QUALITY
        # -------------------------
        story.append(Spacer(1, 10))
        story.append(Paragraph("Data Quality", h2))

        missing = int(df.isnull().sum().sum())
        duplicates = int(df.duplicated().sum())

        if missing == 0 and duplicates == 0:
            story.append(Paragraph("Dataset is CLEAN and analysis-ready.", body))
        else:
            if missing:
                story.append(Paragraph(f"Missing: {missing}", body))
            if duplicates:
                story.append(Paragraph(f"Duplicates: {duplicates}", body))

        # -------------------------
        # INSIGHTS
        # -------------------------
        story.append(Spacer(1, 10))
        story.append(Paragraph("AI Insights", h2))

        if numeric_cols:
            top = numeric_cols[0]

            trend = "Growth" if df[top].mean() > df[top].median() else "Stable"

            story.append(Paragraph(
                f"""
                Primary Metric: {top}<br/>
                Mean: {df[top].mean():.2f}<br/>
                Max: {df[top].max():.2f}<br/>
                Min: {df[top].min():.2f}<br/>
                Variance: {df[top].var():.2f}<br/>
                Trend: {trend}
                """,
                body
            ))

        # -------------------------
        # EXECUTIVE SUMMARY
        # -------------------------
        story.append(PageBreak())
        story.append(Paragraph("Executive Summary", h2))

        summary = f"""
        This AI-generated report analyzes {len(df)} rows and {len(df.columns)} columns.

        Key Insights:
        - Data quality is {'excellent' if missing == 0 else 'needs improvement'}
        - Business KPIs extracted successfully
        - Dataset is suitable for analytics, forecasting, and AI modeling

        Recommendations:
        - Improve missing data handling
        - Track KPIs regularly
        - Apply forecasting models for trends
        - Use AI insights for decision-making
        """

        story.append(Paragraph(summary, body))

        # -------------------------
        # BUILD PDF
        # -------------------------
        doc.build(story)

        st.success("Report generated successfully!")

        with open(tmp.name, "rb") as f:
            st.download_button(
                "⬇ Download Report",
                f,
                file_name="business_report.pdf",
                mime="application/pdf"
            )