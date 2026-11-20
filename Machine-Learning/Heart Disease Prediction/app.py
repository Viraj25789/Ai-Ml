"""Streamlit demo for the educational heart-disease ML project.

This is not a clinical tool and must not be used for diagnosis or treatment.
"""
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "heart_disease_pipeline.joblib"

st.set_page_config(page_title="Heart Disease ML Demo", page_icon="❤️", layout="centered")
st.title("Heart Disease Prediction — ML Demo")
st.warning(
    "Educational demonstration only. This model is not clinically validated, "
    "cannot diagnose heart disease, and must not guide medical decisions. "
    "Consult a qualified healthcare professional about health concerns."
)

@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run 'python train.py' first."
        )
    return joblib.load(MODEL_PATH)

with st.form("prediction_form"):
    st.subheader("Enter example data")
    age = st.number_input("Age (years)", min_value=18, max_value=100, value=45)
    sex = st.selectbox("Sex", ["M", "F"])
    chest_pain = st.selectbox("Chest pain category", ["ATA", "NAP", "TA", "ASY"])
    resting_bp = st.number_input("Resting blood pressure (mm Hg)", min_value=1, max_value=250, value=120)
    cholesterol = st.number_input("Cholesterol (mg/dL)", min_value=1, max_value=700, value=200)
    fasting_bs = st.selectbox("Fasting blood sugar above 120 mg/dL?", [0, 1])
    resting_ecg = st.selectbox("Resting ECG category", ["Normal", "ST", "LVH"])
    max_hr = st.number_input("Maximum heart rate", min_value=40, max_value=250, value=150)
    exercise_angina = st.selectbox("Exercise-induced angina", ["N", "Y"])
    oldpeak = st.number_input("Oldpeak", min_value=-3.0, max_value=8.0, value=0.0, step=0.1)
    st_slope = st.selectbox("ST slope", ["Up", "Flat", "Down"])
    submitted = st.form_submit_button("Run model demo")

if submitted:
    try:
        model = load_model()
        row = pd.DataFrame([{
            "Age": age,
            "Sex": sex,
            "ChestPainType": chest_pain,
            "RestingBP": resting_bp,
            "Cholesterol": cholesterol,
            "FastingBS": fasting_bs,
            "RestingECG": resting_ecg,
            "MaxHR": max_hr,
            "ExerciseAngina": exercise_angina,
            "Oldpeak": oldpeak,
            "ST_Slope": st_slope,
        }])
        prediction = int(model.predict(row)[0])
        probability = float(model.predict_proba(row)[0, 1])
        st.metric("Model-estimated positive class probability", f"{probability:.1%}")
        st.write(
            "The model classified this example as positive."
            if prediction == 1
            else "The model classified this example as negative."
        )
        st.caption(
            "This output is a machine-learning classification, not an estimate "
            "of your actual medical risk. Do not use it to make health decisions."
        )
    except Exception as exc:
        st.error(f"Unable to run the demo: {exc}")
