# ---------------------------
# DASHBOARD
# ---------------------------
if page == "Dashboard":

    # --------- TOP SUMMARY STRIP ---------
    top1, top2, top3 = st.columns([3, 4, 2])

    with top1:
        st.markdown("### Athlete")
        st.markdown(f"**{st.session_state.username}**")
        st.caption("Category: Para Athlete — Wheelchair")

    with top2:
        st.markdown("### Today’s Session")
        st.markdown("**Interval • 45 min**")
        st.success("↑ 3% improvement")

    with top3:
        st.markdown("### Status")
        st.markdown(
            "<div style='width:40px;height:18px;background:#4CAF50;border-radius:6px'></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --------- CORE METRICS ---------
    st.markdown("## Core Metrics")
    m1, m2, m3 = st.columns(3)

    if sessions_df is not None:
        latest = sessions_df.iloc[-1]
        avg_hr = int(latest["Avg_Heart_Rate"])
        fatigue = int(latest.get("Fatigue_Level", 1))
        hydration = int(
            100 * latest.get("Post_Session_Weight", 0) /
            max(1, latest.get("Pre_Session_Weight", 1))
        )
    else:
        avg_hr, fatigue, hydration = 118, 1, 72

    with m1:
        st.metric("Heart Rate", avg_hr)
        st.plotly_chart(
            px.line(y=np.random.normal(avg_hr, 3, 30)),
            use_container_width=True,
            height=150
        )

    with m2:
        st.metric("Fatigue Score", fatigue)
        st.progress(fatigue / 3)

    with m3:
        st.metric("Hydration", f"{hydration}%")
        st.progress(hydration / 100)

    st.markdown("---")

    # --------- DEEP INSIGHTS ---------
    st.markdown("## Deep Insights")
    g1, g2, g3 = st.columns(3)

    with g1:
        hrv = np.random.normal(60, 5, 30)
        st.plotly_chart(px.line(y=hrv), use_container_width=True)

    with g2:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        fatigue_vals = np.random.randint(0, 4, 7)
        st.plotly_chart(px.bar(x=days, y=fatigue_vals),
                         use_container_width=True)

    with g3:
        temp = np.random.normal(33, 1, 30)
        hydration_curve = np.clip(100 - (temp - 33) * 2, 50, 100)
        st.plotly_chart(
            px.scatter(x=temp, y=hydration_curve),
            use_container_width=True
        )

    st.markdown("---")

    # --------- QUICK FATIGUE PREDICTOR ---------
    st.markdown("## Quick Fatigue Predictor")

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

        submitted = st.form_submit_button("Predict")

    if submitted:
        values = [duration, distance, hr, hrv, spo2, temp, sweat, pre_w, post_w]
        prediction = safe_predict_row(values)
        st.success(f"Predicted Fatigue Level: {prediction}")
