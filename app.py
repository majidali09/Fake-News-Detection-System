
import streamlit as st
import pandas as pd
import joblib
from supabase import create_client
from pathlib import Path

st.set_page_config(
    page_title="Fake News Detection System",
    page_icon="🔍",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
h1, h2, h3 {
    color: #17365d;
}
.stButton>button {
    background-color: #17365d;
    color: white;
    border-radius: 8px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)


# Supabase connection
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )


# Load trained ML model
@st.cache_resource
def load_model():
    return joblib.load("fake_news_model.pkl")


st.title("🔍 Fake News Detection System")
st.caption("AI-powered news classification platform")

# Check configuration
try:
    supabase = get_supabase()
    model = load_model()
except Exception as e:
    st.error("Configuration or model loading problem.")
    st.info("Please configure Supabase secrets and check the model file.")
    st.stop()


# Session state
if "user" not in st.session_state:
    st.session_state.user = None


# Login and Signup
if st.session_state.user is None:

    st.markdown("### Welcome to our platform")

    login_tab, signup_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
        st.subheader("User Login")

        email = st.text_input("Email Address", key="login_email")
        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login"):
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = response.user
                st.success("Login successful!")
                st.rerun()
            except Exception:
                st.error("Login failed. Please check your email and password.")

    with signup_tab:
        st.subheader("Create New Account")

        new_email = st.text_input("Email Address", key="signup_email")
        new_password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button("Sign Up"):
            if not new_email or not new_password:
                st.warning("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    response = supabase.auth.sign_up({
                        "email": new_email,
                        "password": new_password
                    })
                    if response.user:
                        st.success(
                            "Account created! Check your email if confirmation is required."
                        )
                except Exception:
                    st.error("Signup failed. Please try again.")


# Logged-in user dashboard
else:

    user = st.session_state.user

    st.sidebar.title("Navigation")
    st.sidebar.write("Logged in as:")
    st.sidebar.caption(user.email)

    page = st.sidebar.radio(
        "Select Page",
        ["Dashboard", "Detect News", "Prediction History"]
    )

    if st.sidebar.button("Logout"):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        st.session_state.user = None
        st.rerun()

    # Dashboard
    if page == "Dashboard":

        st.header("Welcome to Your Dashboard")

        try:
            history = (
                supabase.table("prediction_history")
                .select("*")
                .eq("user_id", str(user.id))
                .execute()
            )
            records = history.data or []

            total = len(records)
            fake_count = sum(
                1 for item in records
                if item["prediction"] == "FAKE"
            )
            real_count = sum(
                1 for item in records
                if item["prediction"] == "REAL"
            )

            col1, col2, col3 = st.columns(3)

            col1.metric("Total News Checked", total)
            col2.metric("Fake News", fake_count)
            col3.metric("Real News", real_count)

        except Exception:
            st.warning("Could not load dashboard statistics.")

        st.info("Use Detect News to analyze a news article.")

    # News Detection
    elif page == "Detect News":

        st.header("AI Fake News Detection")

        news_title = st.text_input("Enter News Title")

        news_text = st.text_area(
            "Paste Complete News Article",
            height=220
        )

        if st.button("Analyze News"):

            if not news_title.strip() or not news_text.strip():
                st.warning("Please enter both title and news article.")

            else:
                combined_text = news_title + " " + news_text

                prediction = int(model.predict([combined_text])[0])
                probabilities = model.predict_proba([combined_text])[0]

                confidence = float(probabilities[prediction]) * 100

                result = "REAL" if prediction == 1 else "FAKE"

                if result == "REAL":
                    st.success("Prediction: REAL NEWS")
                else:
                    st.error("Prediction: FAKE NEWS")

                st.metric("Model Confidence", f"{confidence:.2f}%")

                st.warning(
                    "This is an AI model prediction, not a guarantee "
                    "that the news is factually true or false."
                )

                try:
                    supabase.table("prediction_history").insert({
                        "user_id": str(user.id),
                        "news_title": news_title,
                        "prediction": result,
                        "confidence": round(confidence, 2)
                    }).execute()

                    st.success("Prediction saved to your history.")

                except Exception:
                    st.warning("Prediction completed, but history could not be saved.")

    # Prediction History
    elif page == "Prediction History":

        st.header("Your Prediction History")

        try:
            history = (
                supabase.table("prediction_history")
                .select("*")
                .eq("user_id", str(user.id))
                .order("created_at", desc=True)
                .execute()
            )

            records = history.data or []

            if records:
                df = pd.DataFrame(records)
                st.dataframe(
                    df[["news_title", "prediction", "confidence", "created_at"]],
                    use_container_width=True
                )
            else:
                st.info("No prediction history available yet.")

        except Exception:
            st.error("Unable to load prediction history.")

st.divider()
st.caption("Fake News Detection System | Introduction to Data Science Project")
