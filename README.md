# 🏃 Athlete Monitor Dashboard

A full-stack Streamlit-based athlete performance monitoring system with
machine learning fatigue prediction and SQL-based authentication.

## 🚀 Features
- Secure Login & Registration (SQLite)
- Athlete Performance Dashboard
- Real-time Fatigue Prediction (ML Model)
- Batch Prediction using CSV Upload
- Interactive Visualizations (Plotly)
- Hydration & Fatigue Analysis
- Clean UI with Sidebar Navigation

## 🧠 Technologies Used
- Python
- Streamlit
- Pandas, NumPy
- Plotly
- Scikit-learn
- SQLite
- Joblib

## 📂 Project Structure

```
app.py               # Main Streamlit application
users_db.py          # SQL user authentication logic
fatigue_model.pkl    # Trained ML model
scaler.pkl           # Feature scaler
logo.png             # Application logo
requirements.txt     # Project dependencies
```


## ▶️ How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
## 🎯 Use Case
Designed for monitoring athlete performance and fatigue levels using
physiological sensor data. Suitable for para-athletes and adaptable to
real wearable devices in the future.


## 👤 Author
Mohammed Aqeeb Mohiuddin
Computer Science Student | Machine Learning & Cloud Enthusiast

## 🚀 Live Demo
👉 https://paramonitor.streamlit.app
