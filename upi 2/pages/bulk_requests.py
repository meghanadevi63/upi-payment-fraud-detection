import streamlit as st
import pandas as pd
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# UI Setup
st.set_page_config(layout="wide")

# Hide Sidebar
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    .main .block-container {
        zoom: 1.15;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------- UI HEADERS -------------------------
st.title("📦 Bulk UPI Fraud Check Request")
st.warning("⚠ Please upload a CSV file with only upi_id and Amount columns.")

# ---------------------- FILE UPLOAD ------------------------
uploaded_file = st.file_uploader("📁 Upload your CSV file here", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Step 1: Check column names
        expected_cols = {'upi_id', 'Amount'}
        if set(df.columns) != expected_cols:
            st.error("❌ CSV must contain ONLY these columns: upi_id, Amount.")
        else:
            # Step 2: Validate each row
            df['Amount_Valid'] = pd.to_numeric(df['Amount'], errors='coerce')
            df['upi_id_valid'] = df['upi_id'].astype(str).apply(lambda x: "@" in x and len(x.strip()) > 5)
            df['row_valid'] = df['Amount_Valid'].notnull() & df['upi_id_valid']

            # Step 3: Check if upi_id exists in user data
            dummy_df = pd.read_csv("pages/updated_dummy_upi_user_data.csv")
            valid_upis = set(dummy_df['upi_id'].unique())
            df['exists_in_data'] = df['upi_id'].isin(valid_upis)

            # Final validation
            df['final_valid'] = df['row_valid'] & df['exists_in_data']
            invalid_rows = df[~df['final_valid']]
            valid_rows = df[df['final_valid']]

            if not invalid_rows.empty:
                st.error(f"❌ {len(invalid_rows)} rows failed validation. Please fix these before submission.")
                st.dataframe(invalid_rows[['upi_id', 'Amount', 'Amount_Valid', 'upi_id_valid', 'exists_in_data']])
            else:
                # Step 4: Display validated rows
                st.success("✅ File validated successfully!")
                st.dataframe(valid_rows[['upi_id', 'Amount']])

                # ------------------ PREDICTION ---------------------
                st.markdown("### 🔍 Fraud Prediction Results")

                # Load model and scaler
                model = joblib.load("pages/rf_model.pkl")
                scaler = joblib.load("pages/scaler.pkl")

                result_data = []

                # Prepare for prediction
                with st.spinner("Making predictions..."):
                    for i, row in valid_rows.iterrows():
                        upi_id = row['upi_id']
                        amount = row['Amount']

                        # Get user data for the given UPI ID
                        user_data = dummy_df[dummy_df['upi_id'] == upi_id]
                        if user_data.empty:
                            prediction = "UPI ID not found"
                            result_data.append([upi_id, amount, prediction, datetime.now()])
                        else:
                            user_data = user_data.iloc[0].copy()
                            user_data['transaction_amount'] = amount

                            # Drop 'upi_id' as it's not needed for prediction
                            input_df = pd.DataFrame([user_data.drop('upi_id')])

                            # Ensure the input has the correct number of features (15)
                            if input_df.shape[1] != 15:
                                st.error(f"❌ Input has {input_df.shape[1]} features, but 15 features are expected.")
                                continue

                            input_scaled = scaler.transform(input_df)
                            is_fraud = model.predict(input_scaled)[0]

                            # Store results with prediction
                            prediction = "🔴 FRAUD" if is_fraud else "🟢 SAFE"
                            result_data.append([upi_id, amount, prediction, datetime.now()])

                # -------------------- Display Results in DataFrame ---------------------
                if result_data:
                    result_df = pd.DataFrame(result_data, columns=["UPI ID", "Amount", "Result", "Checked At"])

                    # Custom color for fraud prediction in the Result column
                    def color_fraud(val):
                        if "FRAUD" in val:
                            return 'color: red'
                        else:
                            return 'color: green'

                    # Apply the styling function to the 'Result' column
                    result_df.style.applymap(color_fraud, subset=["Result"])

                    # Display the dataframe with options for search, maximize, and download
                    st.dataframe(result_df, use_container_width=True, height=400)

                    # ------------------- Data Visualization ------------------------
                    st.markdown("### 📊 Data Visualization")

                    # Create a 2x2 grid of subplots
                    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

                    # Fraud vs Non-Fraud Count
                    fraud_count = result_df['Result'].value_counts()
                    fraud_count.plot(kind='bar', ax=axs[0, 0], color=['red', 'green'])
                    axs[0, 0].set_title("Fraud vs Non-Fraud Count")
                    axs[0, 0].set_xlabel("Result")
                    axs[0, 0].set_ylabel("Count")

                    # Correlation heatmap
                    correlation_features = ['device_change', 'transaction_amount', 'vpn_usage', 'location_change', 'ip_address_change']
                    feature_df = dummy_df[correlation_features]
                    corr = feature_df.corr()
                    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=axs[0, 1], fmt=".2f")
                    axs[0, 1].set_title("Feature Correlation Heatmap")

                    # Transaction Amount Distribution
                    sns.histplot(dummy_df['transaction_amount'], kde=True, ax=axs[1, 0])
                    axs[1, 0].set_title("Transaction Amount Distribution")

                    # VPN Usage Distribution
                    sns.countplot(x='vpn_usage', data=dummy_df, ax=axs[1, 1])
                    axs[1, 1].set_title("VPN Usage Distribution")

                    # Adjust layout to prevent overlap
                    plt.tight_layout()

                    # Display the plot
                    st.pyplot(fig)

                   

    except Exception as e:
        st.error(f"❌ Error reading or processing the file: {e}")