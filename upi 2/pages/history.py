import streamlit as st
import psycopg2
import pandas as pd


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

# Hide Sidebar
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    .main .block-container {
        zoom: 1.15;
    }
    h2 {
        color: #2c3e50;
        font-size: 28px;
        font-weight: bold;
    }
    .stExpanderHeader {
        font-size: 18px;
        font-weight: bold;
        color: #16a085;
    }
    .stExpanderContent {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 5px;
    }
    .stDataFrame {
        margin-top: 20px;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)


    

# Heading for Transaction History
st.title("📜 Transaction History")

with st.expander("📜 Click to View Transaction History", expanded=True):
    try:
        # PostgreSQL connection
        conn = psycopg2.connect("postgresql://postgres:postgres2334@localhost:5432/upi_fraud")
        cur = conn.cursor()

        # Query to fetch transaction history
        cur.execute("""
            SELECT upi_id, transaction_amount, result, checked_at
            FROM transactions
            WHERE user_email = %s
            ORDER BY checked_at DESC
        """, (st.session_state.user_email,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Check if history exists and display it
        if rows:
            df = pd.DataFrame(rows, columns=["UPI ID", "Amount", "Result", "Checked At"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No transaction history found.")
        
        # Scroll to the bottom of the page
        st.markdown(
        """
        <script>
        window.scrollTo(0, document.body.scrollHeight);
        </script>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Failed to load history: {e}")

