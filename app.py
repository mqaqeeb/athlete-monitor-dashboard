# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib

from users_db import create_user_table, add_user, validate_user

# ---------------------------
# DB init
# ---------------------------
create_user_table()

# ---------------------------
# Session State
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ---------------------------
# Login / Register
# ---------------------------
def login_screen():
    st.set_page_config(page_title="Login - Athlete Monitor", layout="centered")

    st.image("logo.png", width=140)
    st.markdown("<h1 style='text-align:center;'>Athlete Monitor</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    # LOGIN
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_btn"):
            user = validate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.role = user[3]
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # REGISTER
    with tab2:
        full_name = st.text_input("Full Name", key="reg_name")
        new_user = st.text_input("Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        role = st.selectbox("Register as", ["Athlete", "Coach"], key="reg_role")

        if st.button("Register", key="reg_btn"):
            if add_user(new_user, full_name, new_pass, role):
                st.success("Account created successfully")
            else:
                st.error("Username already exists")

# Show login page
if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ---------------------------
# Main App
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
        return model, scaler
    except:
        return None, None

model, scaler = load_model()

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.image("logo.png", width=120)
st.sidebar.title("Athlete Monitor")
st.sidebar.write(f"👤 {st.session_state.username}")
st.sidebar.write(f"🎭 {st.session_state.role}")

page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Insights", "Alerts", "Batch Predict", "Profile"]
)

uploaded_sessions = st.sidebar.file_uploader(
    "Upload Sensor_Data_1000_Rows.csv", type=["csv"]
)

sessions_df = None
if uploaded_sessions:
    sessions_df = pd.read_csv(uploaded_sessions)

st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ---------------------------
# Header (FIXED)
# ---------------------------
h1, h2 = st.columns([1, 7])
with h1:
    st.image("logo.png", width=65)
with h2:
    st.markdown("<h1 style='margin-bottom:0;'>Athlete Monitor</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<span style='color:gray;'>Welcome, {st.session_state.username} ({st.session_state.role})</span>",
        unsafe_allow_html=True
    )

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------
# DASHBOARD
# ---------------------------
if page == "Dashboard":

    st.subheader("Core Metrics")

    c1, c2, c3 = st.columns(3)

    if sessions_df is not None:
        latest = sessions_df.iloc[-1]
        avg_hr = float(latest["Avg_Heart_Rate"])
        fatigue_est = int(latest.get("Fatigue_Level", 1))
        hydration_pct = int(
            100 * latest["Post_Session_Weight"] /
            max(1, latest["Pre_Session_Weight"])
        )
    else:
        avg_hr, fatigue_est, hydration_pct = 118, 1, 72

    # ✅ DO NOT DISTURB (as requested)
    with c1:
        st.metric("Heart Rate", avg_hr)

    with c2:
        st.metric("Fatigue Level", fatigue_est)
        st.progress(fatigue_est / 3)

    with c3:
        st.metric("Hydration", f"{hydration_pct}%")
        st.progress(hydration_pct / 100)

    # ---------------------------
    # Heart Rate Graph (NEW)
    # ---------------------------
    st.markdown("### Heart Rate Trend")

    if sessions_df is not None:
        hr_series = sessions_df["Avg_Heart_Rate"].tail(30)
    else:
        hr_series = np.random.normal(avg_hr, 4, 30)

    fig = px.line(
        y=hr_series,
        labels={"x": "Time", "y": "Heart Rate (bpm)"},
        height=250
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------
    # Fatigue Predictor (UI FIX)
    # ---------------------------
    st.markdown("---")
    st.markdown("### Quick Fatigue Predictor")

    with st.form("predict_form"):
        left, right = st.columns(2)

        with left:
            duration = st.number_input("Session Duration (min)", 1.0)
            distance = st.number_input("Distance / Reps", 100.0)
            avg_hr_i = st.number_input("Average Heart Rate", 120.0)
            hrv = st.number_input("HR Variability", 55.0)
            spo2 = st.number_input("SpO₂ (%)", 97.0)

        with right:
            skin_temp = st.number_input("Skin Temperature (°C)", 35.0)
            sweat = st.number_input("Sweat Rate (ml/hr)", 500.0)
            pre_w = st.number_input("Pre-session Weight (kg)", 70.0)
            post_w = st.number_input("Post-session Weight (kg)", 69.0)

        submit = st.form_submit_button("Predict Fatigue")

    if submit and model:
        row = [
            duration, distance, avg_hr_i,
            hrv, spo2, skin_temp,
            sweat, pre_w, post_w
        ]
        pred = model.predict(scaler.transform([row]))[0]
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
# ALERTS (SUMMARIZED)
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
st.markdown("<hr><center>© Athlete Monitor</center>", unsafe_allow_html=True)
