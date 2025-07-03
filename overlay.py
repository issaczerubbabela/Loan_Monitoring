import streamlit as st
import pandas as pd
from predict_likelihood import predict_likelihood  # Your function from above

# File paths
csv_file_path = "./processed/processed_borrower.csv"
model_path = "./trained_model_xgb.pkl"

st.title("Borrower Repayment Likelihood")

if st.button("Show Likelihood Prediction"):
    # Predict
    predictions, probabilities = predict_likelihood(csv_file_path, model_path)

    # For now, just show first borrower prediction
    pred_label = predictions[0]
    pred_prob = probabilities[0]

    # Create overlay effect with CSS
    st.markdown(
        """
        <style>
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.75);
            z-index: 9998;
        }
        .popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: white;
            padding: 2em;
            border-radius: 10px;
            z-index: 9999;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # HTML container with overlay and popup
    st.markdown(
        f"""
        <div class="overlay"></div>
        <div class="popup">
            <h3>Repayment Likelihood</h3>
            <p><b>Predicted Label:</b> {pred_label}</p>
            <p><b>Probabilities:</b> {pred_prob}</p>
            <p><i>Explanation: To be added later here...</i></p>
            <button onclick="window.location.reload();">Close</button>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    st.write("Click the button above to see the likelihood as a pop-up.")
