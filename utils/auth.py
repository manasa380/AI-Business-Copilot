import streamlit as st

# -------------------------
# AUTH HELPERS
# -------------------------

def is_logged_in():
    try:
        return getattr(st.user, "is_logged_in", False)
    except:
        return False


def get_user():
    if is_logged_in():
        return st.user
    return None


def require_login():
    if not is_logged_in():
        st.login("google")
        st.stop()