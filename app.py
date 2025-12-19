# app.py
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
# Session States
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ---------------------------
# Login + Register
# ---------------------------
def login_screen():
    st.set_page_config(page_title="Login - Athlete Monitor", layout="centered")
    st.image("logo.png", width=150)

    st.markdown("<h1 style='text-align:center;'>Athlete Monitor Login</h1>",
                unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ----- LOGIN -----
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = validate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.role = user[3]
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # ----- REGISTER -----
    with tab2:
        full_name = st.text_input("Full Name")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        role = st.selectbox("Register as", ["Athlete", "Coach"])

        if st.button("Register"):
            if add_user(new_user, full_name, new_pass, role):
                st.success("Account created successfully")
            else:
                st.error("Username already exists")

# ---------------------------
# Show login if not logged in
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
def load_model():
    try:
        model = joblib.load("fatigue_model.pkl")
        scaler = joblib.load("scaler.pkl")
        return model, scaler, None
    except Exception as e:
        return None, None, str(e)

model, scaler, load_err = load_model()

# ---------------------------
# Sidebar (PAGE DEFINED HERE ✅)
# ---------------------------
st.sidebar.image("logo.png", width=120)
st.sidebar.title("Athlete Monitor")
st.sidebar.write(f"👤 {st.session_state.username}")
st.sidebar.write(f"🎭 Role: {st.session_state.role}")

page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Insights", "Alerts", "Batch Predict", "Profile"]
)

st.sidebar.markdown("---")
if load_err:
    st.sidebar.error("Model load failed")
else:
    st.sidebar.success("Model loaded")

uploaded_sessions = st.sidebar.file_uploader(
    "Upload Sensor_Data_1000_Rows.csv", type=["csv"]
)

sessions_df = None
if uploaded_sessions:
    sessions_df = pd.read_csv(uploaded_sessions)

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ---------------------------
# Header
# ---------------------------
c1, c2 = st.columns([1, 6])
with c1:
    st.image("logo.png", width=80)
with c2:
    st.markdown("<h1>Athlete Monitor</h1>", unsafe_allow_html=True)
    st.caption(f"Welcome, {st.session_state.username}")

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------
# DASHBOARD
# ---------------------------
if page == "Dashboard":

    st.subheader("Core Metrics")

    col1, col2, col3 = st.columns(3)

    if sessions_df is not None:
        latest = sessions_df.iloc[-1]
        avg_hr = latest["Avg_Heart_Rate"]
        fatigue = int(latest.get("Fatigue_Level", 1))
        hydration = int(
            100 * latest["Post_Session_Weight"] /
            max(1, latest["Pre_Session_Weight"])
        )
    else:
        avg_hr, fatigue, hydration = 118, 1, 72

    col1.metric("Heart Rate", avg_hr)
    col2.metric("Fatigue Level", fatigue)
    col2.progress(fatigue / 3)
    col3.metric("Hydration", f"{hydration}%")
    col3.progress(hydration / 100)

    st.markdown("---")

    st.subheader("Quick Fatigue Predictor")

    with st.form("predict"):
        vals = [
            st.number_input("Duration (min)", 1.0),
            st.number_input("Distance / Reps", 100.0),
            st.number_input("Avg HR", 120.0),
            st.number_input("HRV", 55.0),
            st.number_input("SpO2", 97.0),
            st.number_input("Skin Temp", 35.0),
            st.number_input("Sweat Rate", 500.0),
            st.number_input("Pre Weight", 70.0),
            st.number_input("Post Weight", 69.0)
        ]
        submit = st.form_submit_button("Predict")

    if submit and model:
        pred = model.predict(scaler.transform([vals]))[0]
        st.success(f"Predicted Fatigue Level: {pred}")

# ---------------------------
# INSIGHTS
# ---------------------------
elif page == "Insights":
    st.header("Insights")
    if sessions_df is None:
        st.info("Upload CSV to view insights")
    else:
        st.plotly_chart(px.histogram(
            sessions_df, x="Avg_Heart_Rate"),
            use_container_width=True)

# ---------------------------
# ALERTS (BEST PRACTICE FIX ✅)
# ---------------------------
elif page == "Alerts":
    st.header("Alerts")

    if sessions_df is None:
        st.info("Upload CSV to view alerts")
    else:
        recent = sessions_df.tail(10)
        high_fatigue = (recent["Fatigue_Level"] >= 2).sum()

        if high_fatigue > 0:
            st.warning(
                f"⚠ High fatigue detected in {high_fatigue} recent sessions. "
                "Recovery recommended."
            )
        else:
            st.success("No high fatigue detected")

# ---------------------------
# BATCH PREDICT
# ---------------------------
elif page == "Batch Predict":
    st.header("Batch Prediction")
    file = st.file_uploader("Upload CSV", type=["csv"])
    if file and model:
        df = pd.read_csv(file)
        df["Predicted_Fatigue_Level"] = model.predict(
            scaler.transform(df)
        )
        st.success("Prediction completed")
        st.download_button(
            "Download Output",
            df.to_csv(index=False),
            "Batch_Output.csv"
        )

# ---------------------------
# PROFILE
# ---------------------------
elif page == "Profile":
    st.header("Profile")
    st.write(f"Username: {st.session_state.username}")
    st.write(f"Role: {st.session_state.role}")

# ---------------------------
# Footer
# ---------------------------
st.markdown("<hr><center>© Athlete Monitor</center>",
            unsafe_allow_html=True)
