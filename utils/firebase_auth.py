import streamlit as st
import pyrebase

# -----------------------------
# FIREBASE CONFIG
# -----------------------------
firebaseConfig = {
    "apiKey": "AIzaSyB4YKRNqxWbxFpa3wCVwagrcTXPju62VAc",
    "authDomain": "ai-business-copilot-38b3b.firebaseapp.com",
    "projectId": "ai-business-copilot-38b3b",
    "storageBucket": "ai-business-copilot-38b3b.firebasestorage.app",
    "messagingSenderId": "881991223420",
    "appId": "1:881991223420:web:b474f1763cf078fb1f21f9"
}

# -----------------------------
# INIT FIREBASE
# -----------------------------
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()


# -----------------------------
# LOGIN FUNCTION
# -----------------------------
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)

        # Save session
        st.session_state.logged_in = True
        st.session_state.user = email
        st.session_state.firebase_user = user
        st.session_state.role = "user"

        return True

    except Exception as e:
        return False


# -----------------------------
# SIGNUP FUNCTION (optional)
# -----------------------------
def signup(email, password):
    try:
        auth.create_user_with_email_and_password(email, password)
        return True

    except Exception as e:
        return False


# -----------------------------
# LOGOUT FUNCTION
# -----------------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.firebase_user = None
    st.session_state.role = None