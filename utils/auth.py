import streamlit as st

def is_logged_in():
    try:
        return getattr(st.user, "is_logged_in", False)
    except:
        return False


def get_user():
    try:
        if is_logged_in() and hasattr(st.user, "email"):
            return st.user
    except:
        pass
    return None