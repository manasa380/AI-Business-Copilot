
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import html

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.utils import ImageReader

from utils.auth import require_login, get_user


# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="AI Business Intelligence Report",
    page_icon="📄",
    layout="wide"
)

# ==================================================
# AUTHENTICATION
# ==================================================
require_login()
user = get_user()

with st.sidebar:
    st.success(f"👤 {user.name}")
    st.info(f"📧 {user.email}")


# ==================================================
# PAGE HEADER
# ==================================================
st.title("📄 AI Business Intelligence Report")
st.caption(
    "Professional one-page business analytics report "
    "with KPIs, charts, insights and recommendations."
)


# ==================================================
# DATA CHECK
# ==================================================
df = st.session_state.get("df")

if df is None or not isinstance(df, pd.DataFrame) or df.empty:
    st.warning("⚠️ Please upload a dataset first.")
    st.stop()

df = df.copy()

st.subheader("📊 Dataset Preview")
st.dataframe(df.head(), width="stretch")


# ==================================================
# NUMERIC COLUMN DETECTION
# ==================================================
for col in df.columns:

    if pd.api.types.is_numeric_dtype(df[col]):
        continue

    cleaned = (
        df[col]
        .astype("string")
        .str.strip()
        .str.replace(",", "", regex=False)
        .str.replace(
            r"^[₹$€£]\s*",
            "",
            regex=True
        )
    )

    converted = pd.to_numeric(
        cleaned,
        errors="coerce"
    )

    if converted.notna().any():
        df[col] = converted


numeric_cols = [
    col for col in df.select_dtypes(include="number").columns
    if df[col].notna().any()
]

categorical_cols = [
    col for col in df.select_dtypes(
        include=["object", "string", "category"]
    ).columns
    if df[col].nunique(dropna=True) > 0
]


# ==================================================
# DATA QUALITY
# ==================================================
missing = int(df.isnull().sum().sum())
duplicates = int(df.duplicated().sum())

total_cells = len(df) * len(df.columns)

quality_score = (
    100 * (1 - missing / total_cells)
    if total_cells else 0
)

quality_score = max(0, quality_score)


# ==================================================
# REPORT PREVIEW
# ==================================================
st.subheader("📈 Report Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Records", f"{len(df):,}")
c2.metric("Total Columns", len(df.columns))
c3.metric("Missing Values", f"{missing:,}")
c4.metric("Data Quality", f"{quality_score:.1f}/100")

st.info(
    f"Detected {len(numeric_cols)} numeric columns and "
    f"{len(categorical_cols)} categorical columns."
)


# ==================================================
# CHART GENERATION
# ==================================================
def create_chart(chart_type, data=None):

    fig, ax = plt.subplots(figsize=(4.1, 2.35))

    if chart_type == "distribution":

        if data is not None and len(data) > 0:
            ax.hist(
                data,
                bins=15,
                edgecolor="black",
                alpha=0.8
            )

            ax.set_title("Value Distribution")
            ax.set_xlabel("Value")
            ax.set_ylabel("Frequency")

    elif chart_type == "missing":

        missing_by_col = df.isnull().sum()
        missing_by_col = missing_by_col[
            missing_by_col > 0
        ].sort_values(ascending=False).head(8)

        if len(missing_by_col) > 0:
            ax.bar(
                [str(x)[:12] for x in missing_by_col.index],
                missing_by_col.values
            )

            ax.set_title("Missing Values by Column")
            ax.set_ylabel("Missing Count")
            ax.tick_params(axis="x", rotation=30)

        else:
            ax.text(
                0.5, 0.5,
                "No Missing Values",
                ha="center",
                va="center",
                fontsize=13
            )
            ax.set_title("Data Completeness")
            ax.set_axis_off()

    elif chart_type == "correlation":

        corr = df[numeric_cols].corr()

        if corr.notna().values.any():

            image = ax.imshow(
                corr.fillna(0),
                cmap="coolwarm",
                vmin=-1,
                vmax=1
            )

            labels = [str(c)[:10] for c in numeric_cols]

            ax.set_xticks(range(len(labels)))
            ax.set_yticks(range(len(labels)))

            ax.set_xticklabels(
                labels,
                rotation=45,
                ha="right",
                fontsize=7
            )

            ax.set_yticklabels(
                labels,
                fontsize=7
            )

            ax.set_title("Correlation Heatmap")

            fig.colorbar(
                image,
                ax=ax,
                fraction=0.046,
                pad=0.04
            )

        else:
            ax.text(
                0.5, 0.5,
                "Insufficient numeric variation",
                ha="center",
                va="center"
            )
            ax.set_title("Correlation Analysis")
            ax.set_axis_off()

    elif chart_type == "category":

        if categorical_cols:

            col = categorical_cols[0]

            counts = (
                df[col]
                .astype(str)
                .value_counts()
                .head(6)
            )

            ax.bar(
                [str(x)[:12] for x in counts.index],
                counts.values
            )

            ax.set_title(f"Top Categories: {str(col)[:18]}")
            ax.set_ylabel("Count")
            ax.tick_params(axis="x", rotation=30)

        else:
            ax.text(
                0.5, 0.5,
                "No categorical data available",
                ha="center",
                va="center"
            )
            ax.set_axis_off()

    fig.tight_layout()

    buffer = io.BytesIO()

    fig.savefig(
        buffer,
        format="png",
        dpi=120,
        bbox_inches="tight"
    )

    buffer.seek(0)
    plt.close(fig)

    return buffer


# ==================================================
# GENERATE BUSINESS INSIGHTS
# ==================================================
def generate_insights():

    insights = []

    if missing == 0:
        insights.append("The dataset contains no missing values.")
    else:
        insights.append(
            f"The dataset contains {missing} missing values. "
            "Review incomplete records."
        )

    if duplicates == 0:
        insights.append("No duplicate records were detected.")
    else:
        insights.append(
            f"{duplicates} duplicate records were found. "
            "Check whether they should be removed."
        )

    if numeric_cols:

        col = numeric_cols[0]
        values = df[col].dropna()

        if not values.empty:

            mean = values.mean()
            median = values.median()

            insights.append(
                f"{col} has an average value of {mean:,.2f} "
                f"and a median of {median:,.2f}."
            )

            if len(values) > 1:

                std = values.std()

                if mean != 0 and pd.notna(std):
                    cv = abs(std / mean) * 100

                    if cv > 50:
                        insights.append(
                            f"{col} has high relative variation "
                            f"({cv:.1f}% coefficient of variation)."
                        )
                    else:
                        insights.append(
                            f"{col} has relatively moderate variation."
                        )

    if len(numeric_cols) >= 2:
        insights.append(
            "Correlation analysis is available for numeric variables."
        )

    return insights


insights = generate_insights()


# ==================================================
# ONE-PAGE PDF GENERATOR
# ==================================================
def generate_pdf():

    pdf_buffer = io.BytesIO()

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        pdf_buffer,
        pagesize=landscape(A4)
    )

    # ------------------------------
    # COLORS
    # ------------------------------
    navy = colors.HexColor("#142D4E")
    blue = colors.HexColor("#2878B5")
    light_blue = colors.HexColor("#EAF2F8")
    dark = colors.HexColor("#263445")
    grey = colors.HexColor("#64748B")
    green = colors.HexColor("#198754")
    border = colors.HexColor("#D9E2EC")

    # ------------------------------
    # BACKGROUND
    # ------------------------------
    pdf.setFillColor(colors.white)
    pdf.rect(
        0, 0,
        page_width,
        page_height,
        fill=1,
        stroke=0
    )

    margin = 30

    # ------------------------------
    # HEADER
    # ------------------------------
    pdf.setFillColor(navy)
    pdf.rect(
        0,
        page_height - 78,
        page_width,
        78,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 21)

    pdf.drawString(
        margin,
        page_height - 37,
        "BUSINESS INTELLIGENCE REPORT"
    )

    pdf.setFont("Helvetica", 9)

    pdf.drawString(
        margin,
        page_height - 55,
        "Automated Data Analytics | Executive Dashboard"
    )

    pdf.drawRightString(
        page_width - margin,
        page_height - 37,
        "AI BUSINESS COPILOT"
    )

    pdf.drawRightString(
        page_width - margin,
        page_height - 55,
        pd.Timestamp.now().strftime("%d %b %Y")
    )

    # ------------------------------
    # KPI CARDS
    # ------------------------------
    card_y = page_height - 148
    card_h = 53
    gap = 12
    card_w = (page_width - 2 * margin - 3 * gap) / 4

    kpis = [
        ("TOTAL RECORDS", f"{len(df):,}"),
        ("TOTAL COLUMNS", str(len(df.columns))),
        ("MISSING VALUES", f"{missing:,}"),
        ("DATA QUALITY", f"{quality_score:.1f}%")
    ]

    for i, (label, value) in enumerate(kpis):

        x = margin + i * (card_w + gap)

        pdf.setFillColor(light_blue)
        pdf.roundRect(
            x, card_y,
            card_w, card_h,
            7,
            fill=1,
            stroke=0
        )

        pdf.setFillColor(grey)
        pdf.setFont("Helvetica-Bold", 8)

        pdf.drawString(
            x + 10,
            card_y + 35,
            label
        )

        pdf.setFillColor(navy)
        pdf.setFont("Helvetica-Bold", 17)

        pdf.drawString(
            x + 10,
            card_y + 12,
            value
        )

    # ------------------------------
    # CHART SECTION
    # ------------------------------
    chart_top = card_y - 18
    chart_y = 225
    chart_h = 150

    chart_gap = 15
    chart_w = (
        page_width - 2 * margin - 2 * chart_gap
    ) / 3

    charts = []

    # Chart 1: Numeric distribution
    if numeric_cols:

        selected = numeric_cols[0]

        charts.append(
            (
                f"DISTRIBUTION: {selected}",
                create_chart(
                    "distribution",
                    df[selected].dropna()
                )
            )
        )

    else:
        charts.append(
            (
                "DATA DISTRIBUTION",
                create_chart("category")
            )
        )

    # Chart 2: Missing values
    charts.append(
        (
            "DATA COMPLETENESS",
            create_chart("missing")
        )
    )

    # Chart 3: Correlation or category
    if len(numeric_cols) >= 2:

        charts.append(
            (
                "CORRELATION ANALYSIS",
                create_chart("correlation")
            )
        )

    else:

        charts.append(
            (
                "CATEGORY ANALYSIS",
                create_chart("category")
            )
        )

    for i, (heading, chart_buffer) in enumerate(charts):

        x = margin + i * (chart_w + chart_gap)

        pdf.setFillColor(navy)
        pdf.setFont("Helvetica-Bold", 9)

        pdf.drawString(
            x,
            chart_top - 10,
            heading[:42]
        )

        pdf.setStrokeColor(border)

        pdf.roundRect(
            x,
            chart_y,
            chart_w,
            chart_h,
            5,
            fill=0,
            stroke=1
        )

        pdf.drawImage(
            ImageReader(chart_buffer),
            x + 5,
            chart_y + 5,
            width=chart_w - 10,
            height=chart_h - 10,
            preserveAspectRatio=True,
            anchor="c"
        )

    # ------------------------------
    # LOWER SECTION
    # ------------------------------
    section_y = 202

    left_x = margin
    left_w = 370

    right_x = 430
    right_w = page_width - right_x - margin

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        left_x,
        section_y,
        "KEY BUSINESS INSIGHTS"
    )

    pdf.drawString(
        right_x,
        section_y,
        "RECOMMENDATIONS"
    )

    # Paragraph style
    style = ParagraphStyle(
        "ReportBody",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=dark,
        alignment=TA_LEFT
    )

    def draw_paragraph(text, x, y, width, max_height):

        paragraph = Paragraph(
            text,
            style
        )

        actual_w, actual_h = paragraph.wrap(
            width,
            max_height
        )

        paragraph.drawOn(
            pdf,
            x,
            y - actual_h
        )

        return actual_h

    # ------------------------------
    # INSIGHTS
    # ------------------------------
    insight_text = ""

    for item in insights[:4]:
        insight_text += "&#8226; " + html.escape(item) + "<br/>"

    draw_paragraph(
        insight_text,
        left_x,
        section_y - 13,
        left_w,
        65
    )

    # ------------------------------
    # RECOMMENDATIONS
    # ------------------------------
    recommendations = []

    if missing > 0:
        recommendations.append(
            "Review missing values and apply suitable treatment."
        )

    if duplicates > 0:
        recommendations.append(
            "Investigate duplicate records before analysis."
        )

    if not numeric_cols:
        recommendations.append(
            "Add numeric business metrics for KPI analysis."
        )

    if len(numeric_cols) < 2:
        recommendations.append(
            "Include additional numeric metrics for correlation analysis."
        )

    if not recommendations:
        recommendations.append(
            "Continue monitoring business KPIs regularly."
        )

    recommendations.append(
        "Use historical data to evaluate future business trends."
    )

    recommendation_text = ""

    for item in recommendations[:4]:
        recommendation_text += (
            "&#8226; " + html.escape(item) + "<br/>"
        )

    draw_paragraph(
        recommendation_text,
        right_x,
        section_y - 13,
        right_w,
        65
    )

    # ------------------------------
    # NUMERIC SUMMARY
    # ------------------------------
    summary_y = 91

    pdf.setFillColor(navy)
    pdf.setFont("Helvetica-Bold", 10)

    pdf.drawString(
        margin,
        summary_y,
        "NUMERIC KPI SUMMARY"
    )

    if numeric_cols:

        summary_data = []

        for col in numeric_cols[:5]:

            values = df[col].dropna()

            if values.empty:
                continue

            summary_data.append(
                (
                    str(col)[:20],
                    f"{values.mean():,.2f}",
                    f"{values.min():,.2f}",
                    f"{values.max():,.2f}"
                )
            )

        table_x = margin
        table_y = 39

        col_widths = [220, 145, 145, 145]

        headers = [
            "METRIC",
            "AVERAGE",
            "MINIMUM",
            "MAXIMUM"
        ]

        pdf.setFillColor(light_blue)
        pdf.rect(
            table_x,
            table_y + 20,
            sum(col_widths),
            17,
            fill=1,
            stroke=0
        )

        pdf.setFillColor(navy)
        pdf.setFont("Helvetica-Bold", 7)

        current_x = table_x

        for i, header in enumerate(headers):

            pdf.drawString(
                current_x + 5,
                table_y + 26,
                header
            )

            current_x += col_widths[i]

        pdf.setFont("Helvetica", 7)
        pdf.setFillColor(dark)

        for row_index, row in enumerate(summary_data[:2]):

            current_x = table_x
            y = table_y + 9 - row_index * 10

            for i, value in enumerate(row):

                pdf.drawString(
                    current_x + 5,
                    y,
                    str(value)
                )

                current_x += col_widths[i]

    else:

        pdf.setFillColor(grey)
        pdf.setFont("Helvetica", 8)

        pdf.drawString(
            margin,
            58,
            "No numeric KPI columns available."
        )

    # ------------------------------
    # FOOTER
    # ------------------------------
    pdf.setStrokeColor(border)

    pdf.line(
        margin,
        25,
        page_width - margin,
        25
    )

    pdf.setFillColor(grey)
    pdf.setFont("Helvetica", 7)

    pdf.drawString(
        margin,
        13,
        "Generated by AI Business Copilot | Statistical summary based on uploaded data"
    )

    pdf.drawRightString(
        page_width - margin,
        13,
        "Confidential Business Report"
    )

    # Exactly one page
    pdf.showPage()
    pdf.save()

    pdf_buffer.seek(0)

    return pdf_buffer.getvalue()


# ==================================================
# GENERATE REPORT BUTTON
# ==================================================
st.divider()

st.subheader("🚀 Generate Executive Report")

st.write(
    "Generate a professional one-page PDF containing "
    "dataset KPIs, charts, business insights and recommendations."
)

if st.button(
    "🚀 Generate One-Page Business Report",
    type="primary"
):

    try:

        with st.spinner(
            "Creating your professional business report..."
        ):

            pdf_data = generate_pdf()

        st.success("✅ One-page Business Report generated!")

        st.download_button(
            label="⬇️ Download Business Report PDF",
            data=pdf_data,
            file_name="AI_Business_Intelligence_Report.pdf",
            mime="application/pdf",
            type="primary"
        )

    except Exception as e:

        st.error(
            f"❌ Report Generation Error: {str(e)}"
        )
