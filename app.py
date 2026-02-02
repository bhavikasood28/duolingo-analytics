import streamlit as st
import pandas as pd
import requests
from streamlit_lottie import st_lottie


# ----------------------------------------
# LOTTIE + DATA LOADING (CACHED)
# ----------------------------------------
@st.cache_data(show_spinner=False)
def load_lottie(url: str):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except:
        return None

@st.cache_data(show_spinner=True)
def load_data():
    df = pd.read_csv("synthetic_duolingo_events_500k.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ----------------------------------------
# LOAD & CLEAN DATA
# ----------------------------------------
df = load_data()

# Efficient new-user filter:
first_events = (
    df.sort_values("timestamp")
      .groupby("user_id", as_index=False)
      .first()[["user_id", "event_type"]]
)

new_users = first_events.loc[first_events["event_type"] == "signup", "user_id"]

clean_df = df[df["user_id"].isin(new_users)].copy()
st.session_state["clean_df"] = clean_df


# ----------------------------------------
# PAGE CONFIG
# ----------------------------------------
st.set_page_config(
    page_title="Duolingo Analytics Suite",
    page_icon="📘",
    layout="wide"
)


# ----------------------------------------
# SIDEBAR
# ----------------------------------------
st.sidebar.title("🔍 Navigation")
st.sidebar.markdown("""
- 📊 **Funnel Analysis**
- 📈 **Retention Analysis**
- 🔥 **Engagement Metrics**
- 🧪 **A/B Testing**
- 🧩 **User Segmentation**
""")


# ----------------------------------------
# GLOBAL CSS (Optimized)
# ----------------------------------------
st.markdown("""
<style>

    .main { padding: 1.5rem 2rem; }

    h1 { font-weight: 800 !important; letter-spacing: -1px; }
    h2, h3 { font-weight: 700 !important; }

    [data-testid="stSidebar"] {
        background-color: #f0f3f8 !important;
        padding-top: 2rem !important;
    }

    .analytics-card {
        background: white;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        border: 1px solid #e6e6e6;
        margin-bottom: 18px;
        box-shadow: 0 0 4px rgba(0,0,0,0.05);
    }

    table {
        border-radius: 8px !important;
        overflow: hidden !important;
    }

    button[kind="primary"] {
        background: #58CC02 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    footer { visibility: hidden; }
    footer:after {
        content: 'Duolingo-Style Analytics Dashboard — Powered by Streamlit';
        visibility: visible;
        display: block;
        padding: 10px;
        font-size: 0.9rem;
        color: #666;
        text-align: center;
    }

</style>
""", unsafe_allow_html=True)


# ----------------------------------------
# HEADER
# ----------------------------------------
st.title("📘 Duolingo-Style Funnel & Retention Analytics Dashboard")

st.markdown("""
<div style="
    padding: 12px 20px;
    background: #58CC02;
    border-radius: 10px;
    margin-top: 10px;
    margin-bottom: 25px;
    color: white;
    font-size: 1.05rem;
    font-weight: 600;">
    📘 Duolingo-Style Analytics Suite — Learning Insights Dashboard
</div>
""", unsafe_allow_html=True)


# ----------------------------------------
# ANIMATION
# ----------------------------------------
lottie_url = "https://assets9.lottiefiles.com/packages/lf20_q5pk6p1k.json"
lottie_animation = load_lottie(lottie_url)

if lottie_animation:
    st_lottie(lottie_animation, height=180, key="header_lottie")
else:
    st.warning("Animation failed to load.")


# ----------------------------------------
# INTRO TEXT
# ----------------------------------------
st.markdown("""
Welcome to the **Duolingo-Style Analytics Suite**, inspired by analytics used in leading learning apps.

### 📄 Available Modules
- **📊 Funnel Analysis**
- **📈 Retention Analysis**
- **🔥 Engagement Metrics**
- **🧪 A/B Test Simulator**
- **🧩 User Segmentation**

Powered by:
- Streamlit  
- Pandas  
- Plotly  
- Scikit-learn  

Let's dive in! 🚀
""")

st.info("Navigate via the left sidebar to access analytics modules.")
