# Duolingo-Style Funnel & Retention Analytics

This project analyzes user behavior in a learning-app environment inspired by Duolingo.  
Using **500k synthetic event logs**, it explores how users move through onboarding, lessons, and long-term engagement.  
The goal is to understand drop-offs, retention patterns, and what drives ongoing activity.

The project is fully interactive through a **Streamlit dashboard**.

---

## Features

### **1. Funnel Analysis**
- Tracks user progression from **signup → onboarding → lessons → practice**
- Highlights step-to-step conversion rates and major drop-off points

### **2. Retention Analysis**
- Computes **D1, D7, and D30 retention**
- Generates cohort tables and visual retention curves

### **3. Engagement Metrics**
- DAU / WAU / MAU trends  
- Lesson activity  
- Practice frequency and distribution  

### **4. A/B Test Simulator**
- Compares two onboarding variants  
- Calculates activation, completion, and retention differences  
- Includes statistical significance testing  

### **5. User Segmentation**
- KMeans clustering based on user activity  
- Identifies behavior groups such as:
  - Power users  
  - Practice-focused learners  
  - Casual users  
  - Low-engagement users  

---

## 📁 Project Structure
├── app.py # Main Streamlit app
├── 1_Funnel_Analysis.py
├── 2_Retention_Analysis.py
├── 3_Engagement_Metrics.py
├── 4_AB_Test_Simulator.py
├── 5_User_Segmentation.py
├── synthetic_duolingo_events_500k.csv
└── README.md


---

## 📂 Dataset

A synthetic dataset containing:

- User IDs  
- Timestamps  
- Event types (signup, onboarding, lesson_start, lesson_complete, practice, streak_update)

**Total users:** 2,561  
**Total events:** ~500,000  

The dataset mimics typical activity patterns in mobile learning apps.

---

## 🔍 Key Insights (High-Level)

- Onboarding has the **largest drop-off (~41%)**
- Lesson completion is strong *once users start learning*
- Retention is low early on (**D1 ≈ 3%**), similar to real EdTech behavior
- Practice activity strongly correlates with long-term retention
- A/B test variants show **no statistically significant difference** with current sample size
- Segmentation reveals clear groups of learners with distinct engagement styles

---

## ▶️ Running the App

Install dependencies:

```bash
pip install -r requirements.txt
Run Streamlit:
streamlit run app.py

