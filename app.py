'''import streamlit as st
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
        
import streamlit as st
from utils.auth import is_logged_in, get_user

st.set_page_config(
    page_title="AI Business Copilot",
    page_icon="🚀",
    layout="wide"
)

# -------------------------
# LOGIN
# -------------------------
if not is_logged_in():
    st.title("🚀 AI Business Copilot SaaS")
    st.subheader("Sign in with Google to continue")

    st.login("google")
    st.stop()

user = get_user()
if user is None:
    st.stop()

# -------------------------
# SIDEBAR NAVIGATION (THIS WAS MISSING)
# -------------------------
with st.sidebar:
    st.title("📌 Navigation")

    menu = st.selectbox(
        "Choose Module",
        [
            "🏠 Dashboard",
            "📊 Upload Data",
            "🤖 AI Insights",
            "💬 Chat Copilot",
            "📈 Forecasting",
            "🧠 SQL Generator",
            "📄 Business Report"
        ]
    )

    st.divider()
    st.write("👤 User Info")
    st.write(user.name)
    st.write(user.email)

    if st.button("🚪 Logout"):
        st.logout()
        st.rerun()

# -------------------------
# ROUTING SYSTEM (THIS WAS MISSING)
# -------------------------
st.title(menu)

if menu == "🏠 Dashboard":
    st.success(f"Welcome {user.name} 👋")
    st.write("This is your AI Business Copilot dashboard.")

elif menu == "📊 Upload Data":
    st.write("Upload module goes here")

elif menu == "🤖 AI Insights":
    st.write("AI insights module goes here")

elif menu == "💬 Chat Copilot":
    st.write("Chat module goes here")

elif menu == "📈 Forecasting":
    st.write("Forecasting module goes here")

elif menu == "🧠 SQL Generator":
    st.write("SQL generator module goes here")

elif menu == "📄 Business Report":
    st.write("Report generator module goes here")
'''
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
# WAIT FOR SESSION TO LOAD SAFELY
# -------------------------
user = get_user()

# 🔥 IMPORTANT FIX: handle OAuth rerun delay
if is_logged_in() and user is None:
    st.info("Loading your session... please wait")
    st.stop()

# extra safety
if user is None:
    st.error("Login failed. Please refresh the page.")
    st.stop()

# -------------------------
# MAIN DASHBOARD
# -------------------------
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

    st.divider()

    if st.button("🚪 Logout"):
        st.logout()
        st.rerun()