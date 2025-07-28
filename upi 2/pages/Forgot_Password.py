import streamlit as st
import random
import smtplib
import re
from email.mime.text import MIMEText
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ---------- Page Config ----------
st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- Hide sidebar completely ----------
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --------- Constants ---------
DB_URL = "postgresql://postgres:postgres2334@localhost:5432/upi_fraud"

# SQLAlchemy Setup
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

def validate_password(password):
    errors = []
    if len(password) < 8:
        errors.append("❌ Password must be at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        errors.append("❌ Include at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("❌ Include at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        errors.append("❌ Include at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("❌ Include at least one special character.")
    return errors

# ====== Utility Function to Update Password ======
def update_password(email, new_password):
    try:
        # Update password directly in the database (plain text)
        query = text("UPDATE users SET password = :password WHERE email = :email")
        session.execute(query, {"password": new_password, "email": email})
        session.commit()
        return True
    except Exception as e:
        st.error(f"❌ Error updating password in DB: {e}")
        session.rollback()
        return False

# ====== Streamlit Session Setup ======
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = ""
if "email_verified" not in st.session_state:
    st.session_state.email_verified = False
if "email_to_reset" not in st.session_state:
    st.session_state.email_to_reset = ""

st.title("🔐 Forgot Password")

# ====== Step 1: Enter Email & Send OTP ======
if not st.session_state.otp_sent and not st.session_state.email_verified:
    email = st.text_input("Enter your registered Email")

    if st.button("Send OTP"):
        otp = str(random.randint(100000, 999999))
        st.session_state.generated_otp = otp
        st.session_state.otp_sent = True
        st.session_state.email_to_reset = email

        subject = "🔐 OTP for Password Reset"
        body = f"Your OTP for password reset is: {otp}"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "anil231723@gmail.com"  # Replace with your sender email
        msg["To"] = email

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("anil231723@gmail.com", "vaap zhax wwxw lsck")  # Replace / use env vars
            server.sendmail("anil231723@gmail.com", email, msg.as_string())
            server.quit()
            st.success("✅ OTP has been sent to your email.")
        except Exception as e:
            st.error(f"❌ Email sending failed: {e}")

# ====== Step 2: Verify OTP ======
if st.session_state.otp_sent and not st.session_state.email_verified:
    entered_otp = st.text_input("Enter the OTP sent to your email")

    if st.button("Verify OTP"):
        if entered_otp == st.session_state.generated_otp:
            st.session_state.email_verified = True
            st.success("✅ OTP Verified!")
        else:
            st.error("❌ Invalid OTP")

# ====== Step 3: Reset Password Form ======
if st.session_state.email_verified:
    with st.form("reset_password"):
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Reset Password")

    if submit:
        errors = validate_password(new_pass)
        
        if new_pass != confirm_pass:
            st.error("❌ Passwords do not match.")
        elif errors:
            for error in errors:
                st.error(error)
            
        else:
            success = update_password(st.session_state.email_to_reset, new_pass)
            if success:
                st.success("✅ Password updated successfully! You can now log in.")
                # Reset session states
                st.session_state.otp_sent = False
                st.session_state.generated_otp = ""
                st.session_state.email_verified = False
                st.session_state.email_to_reset = ""

                # Add button to navigate to login page
                if st.button("Go to Login"):
                    st.switch_page("./login.py")  # You can handle this logic in your main app to show the login page
                    
            else:
                st.error("❌ Failed to update password.")

