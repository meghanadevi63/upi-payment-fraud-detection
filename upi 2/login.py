import streamlit as st
import psycopg2
import re
import os
import time
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
        
    /* Remove top padding/margin */
        .main > div:first-child {
            padding-top: 10rem !important;
            margin-top: 10rem !important;
        }
        
        /* Fix margins for header section */
        .header-row {
            margin-top: 10px !important;
            padding-top: 10px !important;
        }

        .block-container {
            padding-top: 3rem !important;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------- Constants ----------
DB_URL = "postgresql://postgres:postgres2334@localhost:5432/upi_fraud"
ADMIN_EMAIL = "admin@upi.com"
ADMIN_PASSWORD = "admin@123"
SESSION_FILE = "session.txt"

# ---------- Session Setup ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ---------- Restore session from file if lost on refresh ----------
if not st.session_state.get("user_email") and os.path.exists(SESSION_FILE):
    with open(SESSION_FILE, "r") as f:
        user_email = f.read().strip()
        if user_email:
            st.session_state.user_email = user_email
            st.session_state.logged_in = True

# ---------- Redirect if Already Logged In ----------
if st.session_state.logged_in:
    st.switch_page("pages/home.py")

# ---------- Password Validation ----------
def validate_password_strength(password):
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

# ---------- Title ----------
st.title("🔐 Login")



# ---------- Login Form ----------
with st.form("login_form"):
    st.info("ℹ️ Note: if you are new and not having any password previously, the password you enter here will become your password.")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns([6, 2])  # Adjust as needed
    
    with col1:
        submitted = st.form_submit_button("🔑\u00A0\u00A0Login\u00A0\u00A0")
    
    with col2:
        st.markdown(
            '<a href="/Forgot_Password" target="_self" style="color: #1f77b4; font-size:16px; line-height: 3;">🔒 Forgot Password?</a>',
            unsafe_allow_html=True
        )


# ---------- Authentication Logic ----------
if submitted:
    if not email or not password:
        st.error("Please enter both email and password.")
    elif email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        st.success("✅ Admin login successful!")
        st.session_state.logged_in = True
        st.session_state.user_email = email
        with open(SESSION_FILE, "w") as f:
            f.write(email)
        st.switch_page("pages/admin.py")
    else:
        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE email = %s", (email,))
            result = cur.fetchone()

            if result:
                stored_password = result[0]
                if stored_password is None:
                    errors = validate_password_strength(password)
                    if errors:
                        for err in errors:
                            st.error(err)
                    else:
                        cur.execute("UPDATE users SET password = %s WHERE email = %s", (password, email))
                        conn.commit()
                        st.success("✅ Password set successfully!")
                        time.sleep(1)
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        with open(SESSION_FILE, "w") as f:
                            f.write(email)
                        st.switch_page("pages/home.py")
                elif stored_password == password:
                    st.success("✅ Login successful!")
                    time.sleep(1)
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    with open(SESSION_FILE, "w") as f:
                        f.write(email)
                    st.switch_page("pages/home.py")
                else:
                    st.error("❌ Incorrect password Try again.")
            
            else:
                st.warning("⚠️ No account found with this email, if you have submitted your details for creating account please wait for admin to approve .")

            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Database error: {e}")

# ---------- New User Redirect ----------
col1, col2 = st.columns([5, 2])  # Adjust the ratio to control space between text and button

with col1:
    st.markdown("### 🧑 Don't have an account?")

with col2:
    if st.button("📝 Register Now"):
        st.switch_page("pages/user_account_creation.py")

