# app.py
"""
Athlete Dashboard with SQL Login + Glow Logo + Model Integration
Author: ChatGPT
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly
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

# ---------------------------
# Login + Register UI
# ---------------------------
def login_screen():

    st.set_page_config(page_title="Login - Athlete Monitor", layout="centered")

    # ✅ LOGO (Streamlit native – FIXED)
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
            if validate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("❌ Incorrect username or password")

    # ---- Register ----
    with tab2:
        full_name = st.text_input("Full Name")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Register"):
            if add_user(new_user, full_name, new_pass):
                st.success("🎉 Account created successfully!")
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
st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")

page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Insights", "Alerts", "Batch Predict", "Profile"]
)

st.sidebar.markdown("---")
if load_err:
    st.sidebar.error("⚠ Model Load Failed")
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
# Header (LOGO FIXED)
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

    col1, col2, col3 = st.columns([2, 5, 2])

    with col1:
        # ✅ DYNAMIC ATHLETE NAME
        st.subheader(f"Athlete: {st.session_state.username}")
        st.caption("Category: Para Athlete — Wheelchair")

    with col2:
        st.metric("Today's Session", "Interval • 45 min", delta="↑ 3%")

    with col3:
        st.write("Status")
        st.markdown(
            '<div style="width:36px;height:18px;background:#4CAF50;border-radius:6px;"></div>',
            unsafe_allow_html=True
        )

    st.markdown("### Core Metrics")
    m1, m2, m3 = st.columns(3)

    if sessions_df is not None:
        latest = sessions_df.iloc[-1]
        avg_hr = float(latest["Avg_Heart_Rate"])
        fatigue_est = int(latest.get("Fatigue_Level", 1))
        hydration_pct = int(
            100 * latest.get("Post_Session_Weight", 0) /
            max(1, latest.get("Pre_Session_Weight", 1))
        )
    else:
        avg_hr, fatigue_est, hydration_pct = 118, 1, 72

    with m1:
        st.metric("Heart Rate", avg_hr)
        st.plotly_chart(
            px.line(y=np.random.normal(avg_hr, 3, 30), height=120),
            use_container_width=True
        )

    with m2:
        st.metric("Fatigue Level", fatigue_est)
        st.progress(fatigue_est / 3)

    with m3:
        st.metric("Hydration %", f"{hydration_pct}%")
        st.progress(hydration_pct / 100)

    st.markdown("---")
    st.markdown("### Quick Fatigue Predictor")

    with st.form("predict_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            duration = st.number_input("Duration (min)", 1.0)
            distance = st.number_input("Distance / Reps", 100.0)
            hr = st.number_input("Avg HR", 120.0)

        with c2:
            hrv = st.number_input("HRV", 55.0)
            spo2 = st.number_input("SpO2", 97.0)
            temp = st.number_input("Skin Temp", 35.0)

        with c3:
            sweat = st.number_input("Sweat Rate", 500.0)
            pre_w = st.number_input("Pre Weight", 70.0)
            post_w = st.number_input("Post Weight", 69.0)

        submit = st.form_submit_button("Predict")

    if submit:
        row = [duration, distance, hr, hrv, spo2, temp, sweat, pre_w, post_w]
        st.success(f"Predicted Fatigue Level: {safe_predict_row(row)}")

# ---------------------------
# INSIGHTS
# ---------------------------
elif page == "Insights":
    st.header("Insights")
    if sessions_df is None:
        st.info("Upload CSV to view insights")
    else:
        st.plotly_chart(px.histogram(sessions_df, x="Avg_Heart_Rate"),
                         use_container_width=True)

# ---------------------------
# ALERTS
# ---------------------------
elif page == "Alerts":
    st.header("Alerts")
    if sessions_df is None:
        st.info("Upload CSV to show alerts")
    else:
        for _, row in sessions_df.tail(10).iterrows():
            if row.get("Fatigue_Level", 0) >= 2:
                st.warning("⚠ High Fatigue Detected")

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
            df["Predicted_Fatigue_Level"] = model.predict(scaler.transform(df))
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
    st.write("Role: Athlete / Coach")
    st.write("Version: 1.0")

# ---------------------------
# Footer
# ---------------------------
st.markdown(
    "<hr><center>© Athlete Monitor • SQL Login • ML Powered</center>",
    unsafe_allow_html=True
)

