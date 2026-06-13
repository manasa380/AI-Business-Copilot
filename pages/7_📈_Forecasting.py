import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
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
    page_title="AI Forecasting Engine",
    page_icon="📈",
    layout="wide"
)

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

st.subheader("📊 Dataset Preview")
st.dataframe(df.head(), width='stretch')

# -------------------------
# COLUMN DETECTION
# -------------------------
numeric_cols = df.select_dtypes(include="number").columns.tolist()

date_cols = [
    col for col in df.columns
    if pd.to_datetime(df[col], errors="coerce").notna().mean() > 0.8
]

if not numeric_cols:
    st.error("❌ No numeric columns found")
    st.stop()

if not date_cols:
    st.error("❌ No valid date column found")
    st.stop()

# -------------------------
# USER INPUT
# -------------------------
col1, col2 = st.columns(2)

with col1:
    date_col = st.selectbox("📅 Date Column", date_cols)

with col2:
    target_col = st.selectbox("📊 Target Column", numeric_cols)

forecast_days = st.slider("🔮 Forecast Days", 7, 365, 30)

# -------------------------
# RUN FORECAST
# -------------------------
if st.button("🚀 Generate Forecast"):

    try:
        # -------------------------
        # PREP DATA
        # -------------------------
        temp_df = df[[date_col, target_col]].copy()
        temp_df.columns = ["ds", "y"]

        temp_df["ds"] = pd.to_datetime(temp_df["ds"], errors="coerce")
        temp_df["y"] = pd.to_numeric(temp_df["y"], errors="coerce")

        temp_df = temp_df.dropna()
        temp_df = temp_df.sort_values("ds")

        temp_df = temp_df.groupby("ds", as_index=False)["y"].mean()

        if len(temp_df) < 10:
            st.error("❌ Need at least 10 valid rows")
            st.stop()

        if temp_df["y"].nunique() < 2:
            st.error("❌ Target column has no variation")
            st.stop()

        # -------------------------
        # MODEL
        # -------------------------
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )

        model.fit(temp_df)

        future = model.make_future_dataframe(periods=forecast_days)
        forecast = model.predict(future)

        # -------------------------
        # KPIs
        # -------------------------
        st.subheader("📊 Forecast KPIs")

        current_avg = temp_df["y"].mean()
        forecast_avg = forecast["yhat"].tail(forecast_days).mean()

        c1, c2 = st.columns(2)
        c1.metric("Current Average", f"{current_avg:.2f}")
        c2.metric("Forecast Average", f"{forecast_avg:.2f}")

        # -------------------------
        # FORECAST CHART
        # -------------------------
        st.subheader("📈 Forecast Trend")

        fig = px.line(forecast, x="ds", y="yhat", title="Forecast Trend")

        fig.add_scatter(
            x=temp_df["ds"],
            y=temp_df["y"],
            mode="lines",
            name="Actual"
        )

        st.plotly_chart(fig, width='stretch')

        # -------------------------
        # CONFIDENCE INTERVAL
        # -------------------------
        st.subheader("📉 Prediction Range")

        future_df = forecast.tail(forecast_days)

        fig2 = px.line(future_df, x="ds", y="yhat")

        fig2.add_scatter(
            x=future_df["ds"],
            y=future_df["yhat_upper"],
            name="Upper Bound",
            line=dict(dash="dot")
        )

        fig2.add_scatter(
            x=future_df["ds"],
            y=future_df["yhat_lower"],
            name="Lower Bound",
            line=dict(dash="dot")
        )

        st.plotly_chart(fig2, width='stretch')

        # -------------------------
        # AI INSIGHT
        # -------------------------
        st.subheader("🤖 AI Insight Engine")

        trend_value = (
            forecast["yhat"].iloc[-1] -
            forecast["yhat"].iloc[-forecast_days]
        )

        if trend_value > 0:
            st.success(f"📈 Growth Trend Expected: +{trend_value:.2f}")
        else:
            st.warning(f"📉 Decline Expected: {trend_value:.2f}")

        # -------------------------
        # DATA OUTPUT
        # -------------------------
        with st.expander("📋 Forecast Data"):
            st.dataframe(
                forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(forecast_days),
                width='stretch'
            )

    except Exception as e:
        st.error(f"❌ Forecasting Error: {str(e)}")