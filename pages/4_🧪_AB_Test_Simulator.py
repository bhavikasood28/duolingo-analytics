import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency, norm


# ------------------------------------------------
# CARD COMPONENT
# ------------------------------------------------
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


# ------------------------------------------------
# PAGE TITLE
# ------------------------------------------------
st.title("🧪 A/B Test Simulator")

raw_df = st.session_state["clean_df"]


# ------------------------------------------------
# BULLETPROOF PREPROCESSING (NO .dt ERRORS)
# ------------------------------------------------
@st.cache_data(show_spinner=False)
def prep_ab_data(df):
    df = df.copy()

    # convert timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # STRICT: force date as datetime (not Python date!)
    df["date"] = df["timestamp"].dt.floor("d")

    # infer signup date
    signup_dates = (
        df[df["event_type"] == "signup"]
        .sort_values("timestamp")
        .groupby("user_id")["date"]
        .first()
        .rename("signup_date")
    )

    df = df.merge(signup_dates, on="user_id", how="left")

    # ensure signup_date valid
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")

    # safe day_offset
    df["day_offset"] = (df["date"] - df["signup_date"]).dt.days

    return df


df = prep_ab_data(raw_df)


# ------------------------------------------------
# ASSIGN GROUPS (CACHED & STABLE)
# ------------------------------------------------
@st.cache_data
def assign_groups(user_ids):
    np.random.seed(42)
    return pd.DataFrame({
        "user_id": user_ids,
        "group": np.random.choice(["A", "B"], size=len(user_ids))
    })


users = df["user_id"].unique()
assign_df = assign_groups(users)
df = df.merge(assign_df, on="user_id", how="left")

st.subheader("Group Sizes")
st.write(assign_df["group"].value_counts())


# ------------------------------------------------
# METRICS FUNCTION (NO DATETIME BUGS)
# ------------------------------------------------
def compute_metrics(sub):
    total = sub["user_id"].nunique()
    if total == 0:
        return {"users": 0, "activation_rate": 0, "completion_rate": 0, "d1_retention": 0}

    activated = sub[sub["event_type"] == "lesson_start"]["user_id"].nunique()
    completed = sub[sub["event_type"] == "lesson_complete"]["user_id"].nunique()

    # SAFE D1 retention (never uses .dt)
    d1_users = sub[sub["day_offset"] == 1]["user_id"].nunique()

    return {
        "users": total,
        "activation_rate": activated / total,
        "completion_rate": completed / total,
        "d1_retention": d1_users / total,
    }


A = compute_metrics(df[df["group"] == "A"])
B = compute_metrics(df[df["group"] == "B"])


# ------------------------------------------------
# CONFIDENCE INTERVALS
# ------------------------------------------------
def ci(p, n):
    if n == 0:
        return (0, 0)
    z = norm.ppf(0.975)
    se = np.sqrt(p * (1 - p) / n)
    return (p - z * se, p + z * se)


def format_rate(p, n):
    low, high = ci(p, n)
    return f"{p:.3f} ({low:.3f} – {high:.3f})"


# ------------------------------------------------
# SHOW METRIC CARDS
# ------------------------------------------------
card("Group A Metrics", f"""
<b>Users:</b> {A['users']}<br>
<b>Activation Rate:</b> {format_rate(A['activation_rate'], A['users'])}<br>
<b>Completion Rate:</b> {format_rate(A['completion_rate'], A['users'])}<br>
<b>D1 Retention:</b> {format_rate(A['d1_retention'], A['users'])}
""")

card("Group B Metrics", f"""
<b>Users:</b> {B['users']}<br>
<b>Activation Rate:</b> {format_rate(B['activation_rate'], B['users'])}<br>
<b>Completion Rate:</b> {format_rate(B['completion_rate'], B['users'])}<br>
<b>D1 Retention:</b> {format_rate(B['d1_retention'], B['users'])}
""")


# ------------------------------------------------
# CHI-SQUARE SIGNIFICANCE TEST
# ------------------------------------------------
def chi_square_test(metric):
    a_success = int(A[metric] * A["users"])
    b_success = int(B[metric] * B["users"])

    table = [
        [a_success, A["users"] - a_success],
        [b_success, B["users"] - b_success]
    ]

    chi2, p, _, _ = chi2_contingency(table)
    return p


st.subheader("Statistical Significance (Chi-Square Test)")

results = {
    "activation_rate_p": chi_square_test("activation_rate"),
    "completion_rate_p": chi_square_test("completion_rate"),
    "d1_retention_p": chi_square_test("d1_retention")
}

st.write(results)
