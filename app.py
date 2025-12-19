# app.py
"""
Athlete Monitor Dashboard
SQL Login + ML-Based Fatigue Prediction
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib

# ---------------------------
# SQL Login System
# ---------------------------
from users_db import create_user_table, add_user, validate_user

create_user_table()

# ---------------------------
# Session states
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ---------------------------
# Login + Register UI
# ---------------------------
def login_screen():

    st.set_page_config(page_title="Login - Athlete Monitor", layout="centered")

    st.image("logo.png", width=150)

    st.markdown(
        "<h1 style='text-align:center;'>🔐 Athlete Monitor Login</h1>",
        unsafe_allow_html=True
    )

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ---- Login ----
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = validate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.role = user[1]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("❌ Incorrect username or password")

    # ---- Register ----
    with tab2:
        full_name = st.text_input("Full Name")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        role = st.selectbox(
            "Register as",
            ["Athlete", "Coach"]
        )

        if st.button("Register"):
            if add_user(new_user, full_name, new_pass, role):
                st.success("🎉 Account created successfully! Please login.")
            else:
                st.error("❌ Username already exists")

# ---------------------------
# Show login page if not logged in
# ---------------------------
if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ---------------------------
# Main App Config
# ---------------------------
st.set_page_config(page_title="Athlete Monitor", layout="wide")

# ---------------------------
# Load Model
# ---------------------------
@st.cache_resource
def load_model_and_scaler():
    try:
        model = joblib.load("fatigue_model.pkl")
        scaler = joblib.load("scaler.pkl")
        return model, scaler, None
    except Exception as e:
        return None, None, str(e)

model, scaler, load_err = load_model_and_scaler()

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.image("logo.png", width=140)
st.sidebar.title("Athlete Monitor")
st.sidebar.write(
    f"👤 **{st.session_state.username}** ({st.session_state.role})"
)

page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Insights", "Alerts", "Batch Predict", "Profile"]
)

st.sidebar.markdown("---")
if load_err:
    st.sidebar.error("⚠ Model Load Failed")
    st.sidebar.code(load_err)
else:
    st.sidebar.success("Model Loaded Successfully")

st.sidebar.markdown("---")
uploaded_sessions = st.sidebar.file_uploader(
    "Upload Sensor_Data_1000_Rows.csv", type=["csv"]
)

if uploaded_sessions:
    try:
        sessions_df = pd.read_csv(uploaded_sessions)
        st.sidebar.success(f"Loaded {len(sessions_df)} rows")
    except:
        st.sidebar.error("CSV read error")
        sessions_df = None
else:
    sessions_df = None

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# ---------------------------
# Expected columns
# ---------------------------
EXPECTED_INPUT_COLS = [
    "Session_Duration_mins", "Distance_or_Reps", "Avg_Heart_Rate",
    "HR_Variability", "Oxygen_Saturation", "Skin_Temperature",
    "Sweat_Rate_ml_hr", "Pre_Session_Weight", "Post_Session_Weight"
]

def safe_predict_row(row):
    arr = np.array([row], dtype=float)
    arr_scaled = scaler.transform(arr)
    return int(model.predict(arr_scaled)[0])

# ---------------------------
# Header
# ---------------------------
col_logo, col_title = st.columns([1, 6])

with col_logo:
    st.image("logo.png", width=80)

with col_title:
    st.markdown("<h1>Athlete Monitor</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<span style='color:gray;'>Welcome, {st.session_state.username}</span>",
        unsafe_allow_html=True
    )

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------
# DASHBOARD
# ---------------------------
if page == "Dashboard":
    st.subheader(f"Athlete: {st.session_state.username}")
    st.caption(f"Role: {st.session_state.role}")

# ---------------------------
# INSIGHTS
# ---------------------------
elif page == "Insights":
    st.header("Insights")
    if sessions_df is None:
        st.info("Upload CSV to view insights")
    else:
        st.plotly_chart(
            px.histogram(sessions_df, x="Avg_Heart_Rate"),
            use_container_width=True
        )

# ---------------------------
# ALERTS (SUMMARY – BEST PRACTICE)
# ---------------------------
elif page == "Alerts":
    st.header("Alerts")

    if sessions_df is None:
        st.info("Upload CSV to show alerts")
    else:
        recent = sessions_df.tail(10)
        high_fatigue_count = recent.get(
            "Fatigue_Level", pd.Series()
        ).ge(2).sum()

        if high_fatigue_count > 0:
            st.warning(
                f"⚠ High fatigue detected in {high_fatigue_count} recent sessions. "
                "Rest or recovery is recommended."
            )
        else:
            st.success("✅ No high fatigue detected in recent sessions.")

# ---------------------------
# BATCH PREDICTION
# ---------------------------
elif page == "Batch Predict":
    st.header("Batch Prediction")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded:
        df = pd.read_csv(uploaded)
        if list(df.columns) != EXPECTED_INPUT_COLS:
            st.error("Incorrect CSV column order")
        else:
            df["Predicted_Fatigue_Level"] = model.predict(
                scaler.transform(df)
            )
            st.success("Prediction completed")
            st.download_button(
                "Download CSV",
                df.to_csv(index=False),
                "Batch_Output.csv"
            )

# ---------------------------
# PROFILE
# ---------------------------
elif page == "Profile":
    st.header("User Profile")
    st.write(f"Username: **{st.session_state.username}**")
    st.write(f"Role: **{st.session_state.role}**")
    st.write("Version: 1.1")

# ---------------------------
# Footer
# ---------------------------
st.markdown(
    "<hr><center>© Athlete Monitor • ML Powered Dashboard</center>",
    unsafe_allow_html=True
)
