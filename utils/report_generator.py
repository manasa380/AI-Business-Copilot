from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def generate_report(df, ai_insight):

    file_path = "business_report.pdf"

    doc = SimpleDocTemplate(file_path)

    styles = getSampleStyleSheet()

    story = []

    # ----------------------
    # TITLE
    # ----------------------
    title = Paragraph(
        "AI Business Intelligence Report",
        styles["Title"]
    )

    story.append(title)
    story.append(Spacer(1, 20))

    # ----------------------
    # DATASET INFO
    # ----------------------
    story.append(
        Paragraph(
            "<b>Dataset Summary</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            f"Rows: {df.shape[0]}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"Columns: {df.shape[1]}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 15))

    # ----------------------
    # COLUMN LIST
    # ----------------------
    story.append(
        Paragraph(
            "<b>Columns in Dataset</b>",
            styles["Heading2"]
        )
    )

    cols = ", ".join(df.columns)

    story.append(
        Paragraph(
            cols,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 20))

    # ----------------------
    # AI INSIGHTS
    # ----------------------
    story.append(
        Paragraph(
            "<b>AI Business Insights</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            ai_insight,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 20))

    # ----------------------
    # SAMPLE DATA
    # ----------------------
    story.append(
        Paragraph(
            "<b>Sample Data Preview</b>",
            styles["Heading2"]
        )
    )

    preview = df.head(10).to_string()

    story.append(
        Paragraph(
            f"<pre>{preview}</pre>",
            styles["Code"]
        )
    )

    story.append(PageBreak())

    # ----------------------
    # FOOTER
    # ----------------------
    story.append(
        Paragraph(
            "Generated using AI Business Copilot",
            styles["Italic"]
        )
    )

    doc.build(story)

    return file_path