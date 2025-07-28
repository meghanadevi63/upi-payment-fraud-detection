import streamlit as st 
import pandas as pd
import os
import smtplib
import psycopg2
from email.mime.text import MIMEText
import time 

# Constants
DB_URL = "postgresql://postgres:postgres2334@localhost:5432/upi_fraud"
CSV_FILE = "pages/pending_users.csv"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "anil231723@gmail.com"
SENDER_PASSWORD = "vaap zhax wwxw lsck"  # Use app-specific password

# Session state initialization
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "admin_email" not in st.session_state:
    st.session_state.admin_email = ""
if os.path.exists("session.txt"):
    with open("session.txt", "r") as f:
        email = f.read().strip()
        if email == "admin@upi.com":
            st.session_state.admin_logged_in = True
            st.session_state.admin_email = email

st.set_page_config(page_title="Admin - User Verification", page_icon="🔍")



st.title("🔐 Admin Panel")

import streamlit as st
import os

# Header row with buttons
header_left, header_right = st.columns([9, 6])

with header_right:
    # Create two columns for the buttons (side by side)
    col1, col2 = st.columns(2)
    
    with col1:
        # Profile button
        profile_clicked = st.button("👤 Profile", key="profile", use_container_width=True)
        
    with col2:
        # Logout button
        logout_clicked = st.button("🔒 Logout", key="logout", use_container_width=True)

# Handle button clicks
if profile_clicked:
    st.session_state.show_admin_profile = True

if logout_clicked:
    st.session_state.admin_logged_in = False
    st.session_state.admin_email = ""
    if os.path.exists("session.txt"):
        os.remove("session.txt")
    st.success("✅ Logged out successfully.")
    time.sleep(1)
    st.switch_page("login.py")

# Show admin profile info if the profile button was clicked
if st.session_state.get("show_admin_profile", False):
    st.markdown("---")
    st.subheader("👨‍💼 Admin Profile")
    st.write(f"*Email:* {st.session_state.admin_email}")
    st.write("*Name:* Admin User")
    st.markdown("---")



# --- Tabs ---
tab = "User Verification"

# Utility: Check if user already exists
def is_user_in_database(email):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# Utility: Add user to DB
def add_user_to_database(user_data):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (name, email, phone, pincode, state, mandal, profession, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NULL)
        """, (
            user_data["Name"], user_data["Email"], user_data["Phone"],
            user_data["Pincode"], user_data["State"], user_data["Mandal"], user_data["Profession"]
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ DB Insertion Error: {e}")
        return False

# Utility: Send email
def send_email(to_email, user_name):
    subject = "✅ Account Verified - Set Your Password"
    body = f"""
Hello {user_name},

Your account has been successfully verified. 🎉

You can now login to the platform and set your password on your first login.

Regards,
Admin Team
"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"📧 Email Error: {e}")
        return False

# --- USER VERIFICATION ---
if tab == "User Verification":
    st.subheader("🛂 Pending User Verification")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if df.empty:
            st.info("✅ No pending users to verify.")
        else:
            for index, row in df.iterrows():
                with st.expander(f"👤 {row['Name']} ({row['Email']})"):
                    st.write(f"**📱 Phone:** {row['Phone']}")
                    st.write(f"**📍 Pincode:** {row['Pincode']}")
                    st.write(f"**🗺️ State:** {row['State']}")
                    st.write(f"**🏘️ Mandal:** {row['Mandal']}")
                    st.write(f"**👔 Profession:** {row['Profession']}")

                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if st.button(f"➕ Add to DB", key=f"add_{row['Email']}"):
                            if not is_user_in_database(row["Email"]):
                                success = add_user_to_database(row)
                                if success:
                                    st.success(f"✅ Added {row['Name']} to the database.")
                            else:
                                st.warning(f"⚠️ {row['Name']} already exists in DB.")

                    with col2:
                        if st.button(f"✅ Verify & Notify", key=f"verify_{row['Email']}"):
                            if is_user_in_database(row["Email"]):
                                email_sent = send_email(row["Email"], row["Name"])
                                
                                if email_sent:
                                    st.success(f" ✅ Email sent successfully ")
                                    time.sleep(1)
                                    df.drop(index, inplace=True)
                                    df.to_csv(CSV_FILE, index=False)
                                    st.success(f"🎉 {row['Name']} verified & notified.")
                                    st.rerun()
                            else:
                                st.error("❌ Add the user to the database first.")
    else:
        st.info("📂 No 'pending_users.csv' found.")


# --- HIDE STREAMLIT SIDEBAR AND FOOTER ---
hide_streamlit_style = """
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    #MainMenu, footer {
        
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
