import streamlit as st
from utils.auth import is_logged_in, get_user

st.set_page_config(
    page_title="AI Business Copilot",
    page_icon="🚀",
    layout="wide"
)

# -------------------------
# LOGIN FLOW
# -------------------------
if not is_logged_in():
    st.title("🚀 AI Business Copilot SaaS")
    st.subheader("Sign in with Google to continue")

    st.login("google")
    st.stop()

# -------------------------
# USER AREA
# -------------------------
user = get_user()

# extra safety (prevents edge-case crash)
if user is None:
    st.stop()

st.title("🤖 Dashboard")
st.success(f"Welcome {user.name} 👋")
st.caption(f"Logged in as {user.email}")

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.write("👤 User Info")
    st.write("Name:", user.name)
    st.write("Email:", user.email)

    if st.button("🚪 Logout"):
        st.logout()
        st.rerun()