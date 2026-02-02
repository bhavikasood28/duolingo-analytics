import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from streamlit_lottie import st_lottie

@st.cache_data(show_spinner=False)
def load_lottie(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

# ----------------------------
# CARD COMPONENT
# ----------------------------
def card(title, content):
    st.markdown(
        f"""
        <div class="analytics-card">
            <h3>{title}</h3>
            <div>{content}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ----------------------------
# PAGE TITLE
# ----------------------------
st.title("📈 Retention Analysis")

df = st.session_state["clean_df"]


# ----------------------------
# PREP DATA (FAST & SAFE)
# ----------------------------
@st.cache_data(show_spinner=False)
def prep_retention_data(df):
    df = df.copy()

    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Drop rows where timestamp is invalid
    df = df.dropna(subset=["timestamp"])

    # Convert date properly as datetime64
    df["date"] = df["timestamp"].dt.floor("d")   # ALWAYS datetime64[ns]

    # Infer signup dates per user
    signup_dates = (
        df[df["event_type"] == "signup"]
        .sort_values("timestamp")
        .groupby("user_id")["date"]
        .first()
        .rename("signup_date")
    )

    df = df.merge(signup_dates, on="user_id", how="left")

    # Ensure signup_date is datetime64
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")

    # Compute day offset reliably
    df["day_offset"] = (df["date"] - df["signup_date"]).dt.days

    return df


df = prep_retention_data(df)


# ----------------------------
# DAILY RETENTION
# ----------------------------
st.subheader("Daily Retention (D1, D7, D30)")

total_users = df["user_id"].nunique()

daily_retention = {
    f"D{d}": round(
        df[df["day_offset"] == d]["user_id"].nunique() / total_users * 100, 2
    )
    for d in [1, 7, 30]
}

card("Daily Retention", f"""
<ul>
    <li><b>D1:</b> {daily_retention['D1']}%</li>
    <li><b>D7:</b> {daily_retention['D7']}%</li>
    <li><b>D30:</b> {daily_retention['D30']}%</li>
</ul>
""")

st.write(daily_retention)


# ----------------------------
# COHORT TABLE
# ----------------------------
st.subheader("Cohort Retention Table")

cohort = (
    df.groupby(["signup_date", "day_offset"])["user_id"]
    .nunique()
    .reset_index()
)

cohort_pivot = cohort.pivot(
    index="signup_date",
    columns="day_offset",
    values="user_id"
).sort_index(axis=1)

# Ensure day 0 exists for division
if 0 not in cohort_pivot.columns:
    cohort_pivot[0] = cohort_pivot.max(axis=1)

cohort_ret = cohort_pivot.divide(cohort_pivot[0], axis=0) * 100

st.dataframe(cohort_ret.style.format("{:.1f}%"))


# ----------------------------
# HEATMAP
# ----------------------------
st.subheader("Retention Heatmap")

fig = px.imshow(
    cohort_ret.fillna(0),
    color_continuous_scale="Blues",
    aspect="auto",
)
st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# RETENTION CURVE
# ----------------------------
st.subheader("Average Retention Curve")

curve = cohort_ret.mean().reset_index()
curve.columns = ["day", "retention"]

fig2 = px.line(curve, x="day", y="retention", markers=True)
st.plotly_chart(fig2, use_container_width=True)


# ----------------------------
# ANIMATED RETENTION CURVE
# ----------------------------
fig_anim = px.line(
    curve,
    x="day",
    y="retention",
    markers=True,
    animation_frame="day",
    title="Animated Retention Curve"
)

st.plotly_chart(fig_anim, use_container_width=True)


# ----------------------------
# COHORT ANIMATION
# ----------------------------
cohort_melt = cohort_ret.reset_index().melt(
    id_vars="signup_date",
    var_name="day",
    value_name="retention"
)

fig_cohort_anim = px.scatter(
    cohort_melt,
    x="day",
    y="retention",
    animation_frame="signup_date",
    title="Animated Cohort Retention Over Time",
    range_y=[0, 100]
)

st.plotly_chart(fig_cohort_anim, use_container_width=True)
