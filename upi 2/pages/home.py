import streamlit as st
from streamlit_lottie import st_lottie
import json
import psycopg2
import time
import pandas as pd
import pickle
import os



# ---------- Page Config ----------
st.set_page_config(
    page_title="UPI Fraud Detection",
    layout="wide",
    initial_sidebar_state="collapsed"
)





 #Custom CSS for hover effect for all buttons 
st.markdown("""
    <style>
    .stButton > button {
        background-color:green;
        color: white;
        transition: background-color 0.7s ease;
    }
    .stButton > button:hover {
        background-color: red;
        color:red;
        color: black;
    
    }
    
    </style>
""", unsafe_allow_html=True)

# ---------- Custom CSS for Fixed Bottom Tabs ----------
st.markdown("""
    <style>
    /* Remove top padding/margin */
        .main > div:first-child {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }
        
        /* Fix margins for header section */
        .header-row {
            margin-top: 0px !important;
            padding-top: 0px !important;
        }

        .block-container {
            padding-top: 0rem !important;
        }
    .fixed-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100% 	;
        background-color: background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
        padding: 10px 20px;
        box-shadow: 0 -3px 10px rgba(0,0,0,0.1);
        display: flex;
        justify-content: center;
        gap: 30px;
        z-index: 9999;
    }
    .footer-button {
        background-color:white;
        padding: 8px 20px;
        border-radius: 10px;
        font-weight: 600;
        
        cursor: pointer;
        width:500px;
        
    }
    .footer-button:hover{
    border: 2px solid blue;
    backgorung-color:light green;
    }
    </style>
""", unsafe_allow_html=True)



# ---------- Initialize Session State ----------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = ""

# Your remaining code continues...


# ---------- Hide sidebar completely ----------
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# ---------- Restore session from session.txt on refresh ----------
if "user_email" not in st.session_state or not st.session_state.user_email:
    if os.path.exists("session.txt"):
        with open("session.txt", "r") as f:
            st.session_state.user_email = f.read().strip()
            st.session_state.logged_in = True

# ---------- Load animations ----------
def load_lottie_animation(path):
    try:
        with open(path, "r",encoding="utf-8") as f:
            return json.load(f   )
    except FileNotFoundError:
        return None

tick_lottie = load_lottie_animation("pages/tick.json")
robot = load_lottie_animation("pages/robot.json")

# ---------- Load Model and Scaler ----------
with open("pages/rf_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

with open("pages/scaler.pkl", "rb") as scaler_file:
    scaler = pickle.load(scaler_file)

# ---------- Profile and Logout Buttons ----------
st.markdown("""
    <style>
    .profile-btn, .logout-btn {
        width: 100% !important;
        height: 45px !important;
        font-size: 16px !important;
        font-weight: 600;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)
# Header row with tick animation, heading, and buttons
header_row = st.container()

# Reduce the top margin and padding of the container to move the row up
with header_row:
    # Adding custom CSS to remove padding/margin above the row
    st.markdown("""
        <style>
            .header-row {
                margin-top: 0px;
                padding-top: 0px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Create four columns: one for tick animation, one for heading, two for buttons
    col1, col2, col3, col4 = st.columns([0.5, 6,1, 1])

    # Tick animation
    with col1:
        if tick_lottie:
            st_lottie(tick_lottie, speed=1, width=60, height=60, key="tick")
        else:
            st.warning("⚠️ tick.json not found")

    # Heading
    with col2:
        st.markdown("""
            <h2 style='color: black; font-weight: bold; margin-top: 0px; padding-top: 0px;font-size:50px;'>
            UPI Fraud User Detection System
            </h2>
        """, unsafe_allow_html=True)


    # Profile and Logout buttons
    with col3:
        profile_clicked = st.button("👤 Profile", key="profile", use_container_width=True)
    with col4:
        logout_clicked = st.button("🔒 Logout", key="logout", use_container_width=True)

import streamlit as st
import psycopg2

# Check if profile section should be visible
if "profile_visible" not in st.session_state:
    st.session_state.profile_visible = True

# Toggle visibility based on profile visibility state
if profile_clicked:
    if "user_email" in st.session_state and st.session_state.user_email:
        user_email = st.session_state.user_email
        try:
            conn = psycopg2.connect("postgresql://postgres:postgres2334@localhost:5432/upi_fraud")
            cur = conn.cursor()
            cur.execute("SELECT name, email, phone, profession FROM users WHERE email = %s", (user_email,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result:
                name, email, phone, profession = result

                if st.session_state.profile_visible:
                    # Profile section with Close button
                    st.markdown("""
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h3 style="font-size: 20px; color: #333;">Profile Information</h3>
                            <button onclick="window.location.href='#'" id="close-btn" style="background: none; border: none; font-size: 20px; cursor: pointer; color: red;"></button>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Add Expander to show or hide profile details
                    with st.expander("👤 View Profile Details", expanded=True):
                        st.markdown(f"""
                            <div style="background-color:#f9f9f9; border-radius:10px; padding:20px; box-shadow: 0px 2px 3px rgba(0,0,0,0.1);">
                                <p><strong>Name:</strong> {name}</p>
                                <p><strong>Email:</strong> {email}</p>
                                <p><strong>Phone:</strong> {phone}</p>
               
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("❌ Close Profile"):
                            st.session_state.profile_visible = False

                    # Close profile section
                    
            else:
                st.error("User details not found.")
        except Exception as e:
            st.error(f"Error fetching user details: {e}")
    else:
        st.warning("User not logged in.")

# CSS Styling for the Profile Section and Close X Button
st.markdown("""
    <style>
    #close-btn {
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        color: red;
    }
    .expanderHeader {
        font-size: 18px;
        font-weight: bold;
        color: #2d3748;
        padding-bottom: 10px;
    }
    .expanderBody {
        padding: 10px;
        background-color: #f4f7fa;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

if logout_clicked:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    if os.path.exists("session.txt"):
        os.remove("session.txt")
    st.success("✅ Logged out successfully.")
    time.sleep(0.5)
    st.switch_page("login.py")

# Optional: Add a horizontal line after the header if needed



# ---------- Robot + UPI Input Section ----------
col_ani, col_input = st.columns([1,3])
with col_ani:
    if robot:
        st_lottie(robot, speed=3, height=280,width=350, key="robot")
    else:
        st.warning("⚠️ robot.json not found")



with col_input:
    st.markdown("## 🔎 Check UPI for Fraud")
    upi_id_input = st.text_input("Enter UPI ID:", placeholder="example@upi")
    txn_amount = st.number_input("Enter Transaction Amount", min_value=0.0, format="%.2f")

    if st.button("🚀 Predict Fraud"):
        if not upi_id_input or txn_amount == 0:
            st.warning("Please enter both UPI ID and a valid transaction amount.")
        else:
            # Create placeholders
            container = st.empty()

            # Show both message and animation together inside the container
            with container.container():
                st.markdown("##### 🔄 Loading details from bank...")
                bank_lottie = load_lottie_animation("pages/details from bank.json")
                if bank_lottie:
                    st_lottie(bank_lottie, height=70, speed=1, key="bank_loading")

            time.sleep(2)  # Simulated delay

            # Clear the container (removes both message and animation)
            container.empty()

            # ---------------- Run Prediction ----------------
            try:
                df = pd.read_csv("pages/updated_dummy_upi_user_data.csv")
                record = df[df["upi_id"] == upi_id_input]

                if record.empty:
                    st.error("❌ UPI ID not found in the dataset.")
                else:
                    record = record.drop(columns=["upi_id"])
                    record["transaction_amount"] = txn_amount

                    scaled = scaler.transform(record)
                    prediction = model.predict(scaled)[0]
                    probabilities = model.predict_proba(scaled)[0]
                    confidence = probabilities[prediction]

                    result = "Fraudulent" if prediction == 1 else "Safe"

                    if prediction == 1:
                        st.error(f"🚨 Warning! The UPI ID `{upi_id_input}` is linked to fraudulent behavior.\nProceed with caution. Confidence: {confidence:.2%}")


                    else:
                        st.success(f"✅ No suspicious activity was detected. The UPI ID `{upi_id_input}` is SAFE.\nConfidence: {confidence:.2%}")
                       


                    if "user_email" in st.session_state:
                        user_email = st.session_state.user_email
                        try:
                            conn = psycopg2.connect("postgresql://postgres:postgres2334@localhost:5432/upi_fraud")
                            cur = conn.cursor()
                            cur.execute("""
                                INSERT INTO transactions (user_email, upi_id, transaction_amount, result)
                                VALUES (%s, %s, %s, %s)
                            """, (user_email, upi_id_input, txn_amount, result))
                            conn.commit()
                            cur.close()
                            conn.close()
                        except Exception as e:
                            st.warning(f"Transaction logging failed: {e}")

            except Exception as e:
                st.error(f"Error occurred: {e}")

# ---------- Feature Cards ----------
st.markdown("## 🔐 Key Features")
card1, card2, card3, card4 = st.columns(4)

with card1:
    st.markdown("""
        <div style="background-color:#111927; color:white; padding:20px;
                    border-radius:20px; box-shadow:0 0 15px rgba(0,255,255,0.2);
                    text-align:center; height:200px;">
            <h3>🧠<br>ML-Powered</h3>
            <p>Trained on behavior & transaction data using RandomForest</p>
        </div>
    """, unsafe_allow_html=True)

with card2:
    st.markdown("""
        <div style="background-color:#111927; color:white; padding:20px;
                    border-radius:20px; box-shadow:0 0 15px rgba(0,255,255,0.2);
                    text-align:center; height:200px;">
            <h3>⚡<br>Real-time Scanning</h3>
            <p>Fraud detection in under 2 seconds</p>
        </div>
    """, unsafe_allow_html=True)

with card3:
    st.markdown("""
        <div style="background-color:#111927; color:white; padding:20px;
                    border-radius:20px; box-shadow:0 0 15px rgba(0,255,255,0.2);
                    text-align:center; height:200px;">
            <h3>📁<br>Bulk Upload</h3>
            <p>Check thousands of UPIs with a single CSV</p>
        </div>
    """, unsafe_allow_html=True)

with card4:
    st.markdown("""
        <div style="background-color:#111927; color:white; padding:20px;
                    border-radius:20px; box-shadow:0 0 15px rgba(0,255,255,0.2);
                    text-align:center; height:200px;">
            <h3>📊<br>Insights</h3>
            <p>Transaction patterns, anomalies, and trends</p>
        </div>
    """, unsafe_allow_html=True)


# ---------- Fixed Footer Tabs ----------
st.markdown("""
<div class="fixed-footer">
    <form>
        <button name="tab" value="history" class="footer-button">📜 See my History</button>
        <button name="tab" value="request" class="footer-button">📮 Request Status</button>
    </form>
</div>
""", unsafe_allow_html=True)

# Use session state to track tab selection
if "tab" in st.query_params:
    st.session_state.active_tab = st.query_params["tab"]

active_tab = st.session_state.active_tab

if active_tab == "history":
   st.session_state.redirecting = True
   st.switch_page("pages/history.py")
elif active_tab == "request":
    # Switch to the Bulk Request Page
    st.session_state.redirecting = True
    st.switch_page("pages/bulk_requests.py")


# ---------- Footer ----------
st.markdown("---")
st.markdown("<p style='text-align: center; color: grey;'>© 2025 | UPI Fraud Detection | Built with 💙 by Students</p>", unsafe_allow_html=True)
