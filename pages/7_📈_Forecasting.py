
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet
from utils.auth import require_login, get_user

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="AI Forecasting Engine",
    page_icon="📈",
    layout="wide"
)

# -------------------------
# AUTH CHECK
# -------------------------
require_login()
user = get_user()

# -------------------------
# SIDEBAR USER INFO
# -------------------------
with st.sidebar:
    st.success(f"👤 {user.name}")
    st.info(f"📧 {user.email}")

# -------------------------
# TITLE
# -------------------------
st.title("📈 AI Forecasting Engine (Pro)")
st.caption("Advanced Time Series Forecasting using Prophet")

# -------------------------
# DATA CHECK
# -------------------------
df = st.session_state.get("df")

if df is None or not isinstance(df, pd.DataFrame) or df.empty:
    st.warning("⚠️ Upload dataset first")
    st.stop()

df = df.copy()

st.subheader("📊 Dataset Preview")
st.dataframe(df.head(), width="stretch")

# -------------------------
# NUMERIC COLUMN DETECTION
# -------------------------
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

    if converted.notna().any():
        df[col] = converted

numeric_cols = [
    col for col in df.select_dtypes(include="number").columns
    if df[col].notna().sum() >= 2
]

# -------------------------
# DATE COLUMN DETECTION
# -------------------------
date_cols = []

date_data = {}

for col in df.columns:

    if pd.api.types.is_numeric_dtype(df[col]):
        continue

    try:
        parsed = pd.to_datetime(
            df[col],
            errors="coerce",
            format="mixed",
            dayfirst=True
        )
    except (TypeError, ValueError):
        parsed = pd.to_datetime(
            df[col],
            errors="coerce",
            dayfirst=True
        )

    valid_ratio = parsed.notna().mean()

    if valid_ratio >= 0.7:
        date_cols.append(col)
        date_data[col] = parsed

# -------------------------
# DETECTION INFORMATION
# -------------------------
with st.expander("🔍 Detected Dataset Columns"):
    st.write("Numeric Columns:", numeric_cols)
    st.write("Date Columns:", date_cols)

# -------------------------
# VALIDATION
# -------------------------
if not numeric_cols:
    st.error(
        "❌ No numeric columns found. "
        "Upload a dataset containing values such as Sales, Revenue, "
        "Price, Quantity or Profit."
    )
    st.stop()

if not date_cols:
    st.error(
        "❌ No valid date column found. "
        "Your dataset needs a date column for time-series forecasting."
    )
    st.stop()

# -------------------------
# USER INPUT
# -------------------------
st.subheader("⚙️ Forecast Configuration")

col1, col2 = st.columns(2)

with col1:
    date_col = st.selectbox(
        "📅 Select Date Column",
        date_cols
    )

with col2:
    target_col = st.selectbox(
        "📊 Select Target Column",
        numeric_cols
    )

frequency_option = st.selectbox(
    "📆 Forecast Frequency",
    ["Daily", "Weekly", "Monthly"]
)

frequency_map = {
    "Daily": "D",
    "Weekly": "W",
    "Monthly": "MS"
}

frequency = frequency_map[frequency_option]

forecast_periods = st.slider(
    "🔮 Number of Future Periods",
    min_value=7,
    max_value=365,
    value=30
)

if frequency_option == "Weekly":
    st.caption("Forecast periods represent weeks.")
elif frequency_option == "Monthly":
    st.caption("Forecast periods represent months.")
else:
    st.caption("Forecast periods represent days.")

# -------------------------
# RUN FORECAST
# -------------------------
if st.button("🚀 Generate Forecast", type="primary"):

    try:

        # -------------------------
        # PREPARE DATA
        # -------------------------
        temp_df = pd.DataFrame({
            "ds": date_data[date_col],
            "y": df[target_col]
        })

        temp_df["y"] = pd.to_numeric(
            temp_df["y"],
            errors="coerce"
        )

        temp_df = temp_df.dropna()

        temp_df = temp_df.sort_values("ds")

        # Combine duplicate dates
        temp_df = temp_df.groupby(
            "ds",
            as_index=False
        )["y"].mean()

        if len(temp_df) < 10:
            st.error(
                "❌ Need at least 10 valid date-value records "
                "to generate a forecast."
            )
            st.stop()

        if temp_df["y"].nunique() < 2:
            st.error(
                "❌ Target column has no variation. "
                "Choose a column containing different numeric values."
            )
            st.stop()

        # -------------------------
        # RESAMPLE DATA
        # -------------------------
        temp_df = (
            temp_df
            .set_index("ds")
            .resample(frequency)["y"]
            .mean()
            .dropna()
            .reset_index()
        )

        if len(temp_df) < 10:
            st.error(
                "❌ Not enough historical observations at the "
                f"selected {frequency_option.lower()} frequency. "
                "Try a more detailed frequency or provide more data."
            )
            st.stop()

        if temp_df["y"].nunique() < 2:
            st.error("❌ Target values have insufficient variation.")
            st.stop()

        # -------------------------
        # PROPHET MODEL
        # -------------------------
        st.info("⏳ Training forecasting model...")

        date_range = (
            temp_df["ds"].max() - temp_df["ds"].min()
        ).days

        model = Prophet(
            yearly_seasonality=date_range >= 365,
            weekly_seasonality=(
                frequency_option == "Daily" and len(temp_df) >= 14
            ),
            daily_seasonality=False,
            interval_width=0.95
        )

        model.fit(temp_df)

        # -------------------------
        # GENERATE FUTURE DATA
        # -------------------------
        future = model.make_future_dataframe(
            periods=forecast_periods,
            freq=frequency
        )

        forecast = model.predict(future)

        future_df = forecast.tail(forecast_periods).copy()

        if future_df.empty:
            st.error("Unable to generate future predictions.")
            st.stop()

        # -------------------------
        # FORECAST KPIs
        # -------------------------
        st.subheader("📊 Forecast KPIs")

        current_avg = temp_df["y"].mean()
        forecast_avg = future_df["yhat"].mean()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Historical Average",
            f"{current_avg:,.2f}"
        )

        c2.metric(
            "Forecast Average",
            f"{forecast_avg:,.2f}"
        )

        percentage_change = (
            ((forecast_avg - current_avg) / abs(current_avg)) * 100
            if current_avg != 0 else 0
        )

        c3.metric(
            "Expected Change",
            f"{percentage_change:+.2f}%"
        )

        # -------------------------
        # FORECAST CHART
        # -------------------------
        st.subheader("📈 Forecast Trend")

        fig = px.line(
            forecast,
            x="ds",
            y="yhat",
            title=f"{target_col} Forecast"
        )

        fig.add_scatter(
            x=temp_df["ds"],
            y=temp_df["y"],
            mode="markers+lines",
            name="Historical Actual"
        )

        fig.add_scatter(
            x=future_df["ds"],
            y=future_df["yhat_upper"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            name="Upper Range"
        )

        fig.add_scatter(
            x=future_df["ds"],
            y=future_df["yhat_lower"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(100,150,200,0.15)",
            name="Prediction Range"
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title=target_col,
            hovermode="x unified"
        )

        st.plotly_chart(fig, width="stretch")

        # -------------------------
        # CONFIDENCE INTERVAL
        # -------------------------
        st.subheader("📉 Prediction Range (95%)")

        fig2 = px.line(
            future_df,
            x="ds",
            y="yhat",
            title="Future Prediction with Confidence Bounds"
        )

        fig2.add_scatter(
            x=future_df["ds"],
            y=future_df["yhat_upper"],
            mode="lines",
            name="Upper Bound",
            line=dict(dash="dot")
        )

        fig2.add_scatter(
            x=future_df["ds"],
            y=future_df["yhat_lower"],
            mode="lines",
            name="Lower Bound",
            line=dict(dash="dot")
        )

        st.plotly_chart(fig2, width="stretch")

        # -------------------------
        # AI INSIGHTS
        # -------------------------
        st.subheader("🤖 Forecast Insights")

        historical_prediction = forecast[
            forecast["ds"] <= temp_df["ds"].max()
        ]

        baseline = historical_prediction["yhat"].iloc[-1]
        final_prediction = future_df["yhat"].iloc[-1]

        trend_value = final_prediction - baseline

        if trend_value > 0:
            st.success(
                f"📈 Growth Trend Expected: +{trend_value:,.2f}"
            )
        elif trend_value < 0:
            st.warning(
                f"📉 Decline Expected: {trend_value:,.2f}"
            )
        else:
            st.info("➡️ Stable trend expected.")

        st.caption(
            "Forecasts are statistical estimates, not guaranteed outcomes."
        )

        # -------------------------
        # FORECAST DATA
        # -------------------------
        with st.expander("📋 View Forecast Data"):

            output = future_df[
                ["ds", "yhat", "yhat_lower", "yhat_upper"]
            ].copy()

            output.columns = [
                "Date",
                "Predicted Value",
                "Lower Bound",
                "Upper Bound"
            ]

            st.dataframe(
                output,
                width="stretch"
            )

            csv = output.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇️ Download Forecast CSV",
                data=csv,
                file_name="forecast_results.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"❌ Forecasting Error: {str(e)}")
