import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
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

# ---------------------------------------------
# CARD COMPONENT
# ---------------------------------------------
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


# ---------------------------------------------
# PAGE TITLE
# ---------------------------------------------
st.title("🧩 User Segmentation")


# ---------------------------------------------
# PREP & FEATURE ENGINEERING (CACHED)
# ---------------------------------------------
@st.cache_data(show_spinner=False)
def prepare_segmentation_data(df):
    df = df.copy()

    # All metrics in one grouped aggregation (fastest)
    metrics = df.groupby("user_id").agg(
        total_events=("event_type", "size"),
        lessons_completed=("event_type", lambda x: (x == "lesson_complete").sum()),
        practice_events=("event_type", lambda x: (x == "practice").sum()),
    )

    return metrics


df_raw = st.session_state["clean_df"]
metrics = prepare_segmentation_data(df_raw)


# ---------------------------------------------
# SUMMARY & BASIC VIS
# ---------------------------------------------
st.subheader("Basic Segmentation Overview")

card(
    "User Activity Summary",
    metrics.describe().to_html()
)

st.write("### Total Events Distribution")
st.bar_chart(metrics["total_events"])


# ---------------------------------------------
# KMEANS SEGMENTATION
# ---------------------------------------------
st.subheader("KMeans Segmentation")

n_clusters = st.slider("Number of Clusters", 2, 8, 4)

# Standardize features
scaler = StandardScaler()
scaled = scaler.fit_transform(metrics)

# Fit KMeans
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
metrics["cluster"] = kmeans.fit_predict(scaled)


# ---------------------------------------------
# CLUSTER CENTROIDS
# ---------------------------------------------
centroids = pd.DataFrame(
    scaler.inverse_transform(kmeans.cluster_centers_),
    columns=metrics.columns[:-1]
)
centroids["cluster"] = centroids.index

card("Cluster Centroids (Unscaled)", centroids.to_html(index=False))


# ---------------------------------------------
# SEGMENTATION SCATTER PLOT
# ---------------------------------------------
st.subheader("Segmentation Visualization")

fig = px.scatter(
    metrics,
    x="total_events",
    y="practice_events",
    color=metrics["cluster"].astype(str),
    hover_data=["lessons_completed"],
    title="User Segmentation Scatter Plot",
)
st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------
# OPTIONAL 3D VISUALIZATION
# ---------------------------------------------
if st.checkbox("Show 3D Segmentation Plot"):
    fig3d = px.scatter_3d(
        metrics,
        x="total_events",
        y="practice_events",
        z="lessons_completed",
        color=metrics["cluster"].astype(str),
        title="3D Segmentation View",
    )
    st.plotly_chart(fig3d, use_container_width=True)


# ---------------------------------------------
# SEGMENT LABELING (AUTO)
# ---------------------------------------------
st.subheader("Suggested Segment Labels")

def label_cluster(row, centroids):
    # Simple heuristic based on activity intensity
    if row["lessons_completed"] > centroids["lessons_completed"].mean():
        return "Power Learner"
    if row["practice_events"] > centroids["practice_events"].mean():
        return "Practice Focused"
    if row["total_events"] < centroids["total_events"].mean() * 0.4:
        return "Low Engagement"
    return "Casual Learner"

metrics["segment"] = metrics.apply(label_cluster, axis=1, centroids=centroids)

st.write(metrics["segment"].value_counts())

card(
    "Example Segment Labels",
    """
    <ul>
        <li><b>Power Learners</b> – high lessons completed</li>
        <li><b>Practice-Focused</b> – lots of practice sessions</li>
        <li><b>Casual Learners</b> – moderate activity</li>
        <li><b>Low Engagement</b> – minimal interaction</li>
    </ul>
    """
)
