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
st.title("🔥 Engagement Metrics")

raw_df = st.session_state["clean_df"]


# ----------------------------
# PREPROCESS (CACHED)
# ----------------------------
@st.cache_data(show_spinner=False)
def prep_engagement_data(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    df["week"] = df["timestamp"].dt.isocalendar().week.astype(int)
    df["month"] = df["timestamp"].dt.to_period("M").astype(str)
    return df


df = prep_engagement_data(raw_df)


# ----------------------------
# DAU / WAU / MAU
# ----------------------------
st.subheader("DAU / WAU / MAU")

dau = df.groupby("date")["user_id"].nunique().reset_index()
wau = df.groupby("week")["user_id"].nunique().reset_index()
mau = df.groupby("month")["user_id"].nunique().reset_index()

fig_dau = px.line(dau, x="date", y="user_id", title="Daily Active Users (DAU)")
fig_wau = px.line(wau, x="week", y="user_id", title="Weekly Active Users (WAU)")
fig_mau = px.line(mau, x="month", y="user_id", title="Monthly Active Users (MAU)")

st.plotly_chart(fig_dau, use_container_width=True)
st.plotly_chart(fig_wau, use_container_width=True)
st.plotly_chart(fig_mau, use_container_width=True)


# ----------------------------
# LESSON ENGAGEMENT
# ----------------------------
st.subheader("Lesson Engagement")

lesson_df = df[df["event_type"].isin(["lesson_start", "lesson_complete"])]

lesson_counts = (
    lesson_df.groupby(["user_id", "event_type"])
    .size()
    .unstack(fill_value=0)
)

card(
    "Lesson Activity Summary",
    lesson_counts.describe().to_html(),
)


# ----------------------------
# PRACTICE DISTRIBUTION
# ----------------------------
st.subheader("Practice Distribution")

practice_freq = df[df["event_type"] == "practice"].groupby("user_id").size()

practice_hist = (
    practice_freq.value_counts()
    .sort_index()
    .reset_index()
)

# rename robustly no matter what Pandas names the columns
practice_hist.columns = ["practice_count", "user_count"]

st.write(practice_hist.head())  # debug if needed

fig_practice = px.bar(
    practice_hist,
    x="practice_count",
    y="user_count",
    title="Distribution of Practice Counts",
)

st.plotly_chart(fig_practice, use_container_width=True)


