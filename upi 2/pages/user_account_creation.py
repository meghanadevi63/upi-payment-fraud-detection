import streamlit as st
import pandas as pd
import os
import re
import psycopg2

# ---------- Page Config ----------
st.set_page_config(
    page_title="User Registration",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- Hide Sidebar Completely ----------
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        footer {visibility: hidden;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Constants ----------
CSV_FILE = "pending_users.csv"
DB_URL = "postgresql://postgres:postgres2334@localhost:5432/upi_fraud"

st.title("📝 User Registration Form")

# ---------- Validation Utilities ----------
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10

def is_valid_pincode(pincode):
    return pincode.isdigit() and len(pincode) == 6
def is_valid_text_field(value):
    return bool(re.match(r'^[A-Za-z ]+$', value))

# ---------- File/DB Utilities ----------
def is_duplicate(email, phone):
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return ((df['Email'] == email) | (df['Phone'] == phone)).any()
    return False

def is_user_in_database(email, phone):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s OR phone = %s", (email, phone))
        exists = cur.fetchone() is not None
        cur.close()
        conn.close()
        return exists
    except Exception as e:
        st.error(f"❌ Database error: {str(e)}")
        return False

def append_to_csv(user_data):
    df = pd.DataFrame([user_data])
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

# ---------- Streamlit Form ----------
with st.form("user_registration_form"):
    st.markdown("📋 Please fill out all required fields to register.")

    name = st.text_input("Full Name *")
    email = st.text_input("Email *")
    phone = st.text_input("Phone (10 digits) *")
    pincode = st.text_input("Pincode (6 digits) *")
    state = st.text_input("State *")
    mandal = st.text_input("Mandal *")
    profession = st.text_input("Profession *")
    photo_filename = st.file_uploader("Upload Photo (Optional)", type=["jpg", "png"])

    submit_button = st.form_submit_button("Submit")

# ---------- Submission Logic ----------
if submit_button:
    if not all([name, email, phone, pincode, state, mandal, profession]):
        st.error("❌ All fields (except photo) are required.")
    elif not is_valid_email(email):
        st.error("❌ Invalid email format.")
    elif not is_valid_phone(phone):
        st.error("❌ Phone must be 10 digits.")
    elif not is_valid_pincode(pincode):
        st.error("❌ Pincode must be 6 digits.")
    elif not is_valid_text_field(name):
        st.error("❌ Invalid Name .")
    elif not is_valid_text_field(state):
        st.error("❌ Invalid State.")
    elif not is_valid_text_field(mandal):
        st.error("❌ Invalid Mandal.")
    elif not is_valid_text_field(profession):
        st.error("❌ Invalid profession.")
    elif is_duplicate(email, phone):
        st.warning("⚠️ You have already submitted your details. Please wait for Admin verification.")
    elif is_user_in_database(email, phone):
        st.warning("⚠️ An account with these details already exists Please Login below .")
    else:
        user_data = {
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Pincode": pincode,
            "State": state,
            "Mandal": mandal,
            "Profession": profession
            
        }
        append_to_csv(user_data)
        st.success("✅ Registration successful! Awaiting admin approval and verification.You will get notified Once admin verified Your details ")

# ---------- Already Have Account ----------
st.markdown("---")
st.markdown("🔐 Already have an account?")
if st.button("Login Here"):
    st.switch_page("./login.py")  # Redirect to login.py (outside pages/)

