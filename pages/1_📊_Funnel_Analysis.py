import streamlit as st
import pandas as pd
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
# HEADER ANIMATION (CACHED)
# ----------------------------
@st.cache_data(show_spinner=False)
def get_funnel_lottie():
    return load_lottie("https://assets10.lottiefiles.com/packages/lf20_svy4ivvy.json")

lottie_funnel = get_funnel_lottie()
st_lottie(lottie_funnel, height=120)


# ----------------------------
# REUSABLE CARD COMPONENT
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
st.title("📊 Funnel Analysis")

df = st.session_state["clean_df"]

st.subheader("Running Funnel Analysis on Cleaned New-User Dataset")


# ----------------------------
# FUNNEL STEPS (STATIC)
# ----------------------------
FUNNEL_STEPS = [
    "signup",
    "onboarding_step",
    "lesson_start",
    "lesson_complete",
    "practice",
    "streak_update",
]


# ----------------------------
# COMPUTE FUNNEL COUNTS (FAST)
# ----------------------------
# One filter → one aggregation (much faster than looping)
stage_users = (
    df[df["event_type"].isin(FUNNEL_STEPS)]
    .groupby("event_type")["user_id"]
    .nunique()
    .reindex(FUNNEL_STEPS, fill_value=0)
    .to_dict()
)

st.subheader("Funnel Counts")
st.write(stage_users)

# Plotting
funnel_df = (
    pd.DataFrame({"stage": FUNNEL_STEPS, "users": [stage_users[s] for s in FUNNEL_STEPS]})
    .set_index("stage")
)
st.bar_chart(funnel_df)


# ----------------------------
# STEP-TO-STEP CONVERSION RATES
# ----------------------------
conversion_rates = {}
previous_users = None

for step in FUNNEL_STEPS:
    users = stage_users[step]
    if previous_users is None:  # first step (signup)
        conversion_rates[step] = 100.0
    else:
        conversion_rates[step] = round((users / previous_users) * 100, 2) if previous_users != 0 else 0
    previous_users = users

st.subheader("Step-to-Step Conversion Rates (%)")
st.write(conversion_rates)


# Optionally show a card UI tile
card(
    "📉 Funnel Summary",
    f"""
    <ul>
    <li><b>Signup:</b> {stage_users['signup']} users</li>
    <li><b>Final Stage:</b> {list(stage_users.values())[-1]} users</li>
    <li><b>Total Drop-off:</b> {stage_users['signup'] - list(stage_users.values())[-1]}</li>
    </ul>
    """
)
