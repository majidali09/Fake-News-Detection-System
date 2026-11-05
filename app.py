import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
from supabase import create_client

st.set_page_config(
    page_title="TruthLens | Fake News Detection",
    page_icon="🔍",
    layout="wide"
)

# ================= DESIGN =================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#f3f7ff,#eaf4f8,#e9f7f5);
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}
h1,h2,h3 {
    color: #142b4a;
}
.hero {
    background: linear-gradient(115deg,#102747,#145b7c,#148b91);
    padding: 30px;
    border-radius: 22px;
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    color: white !important;
    font-size: 38px;
}
.hero p {
    color: #e4f5ff;
}
.auth-card {
    background: white;
    border: 1px solid #dfe9f2;
    border-radius: 19px;
    padding: 22px;
    box-shadow: 0 9px 26px rgba(20,50,80,.07);
}
.stat-card {
    background: white;
    border: 1px solid #e0eaf2;
    border-radius: 17px;
    padding: 20px;
    min-height: 110px;
}
.stat-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 700;
}
.stat-value {
    color: #142b4a;
    font-size: 32px;
    font-weight: 800;
}
.result-real {
    background: #e1f8eb;
    border: 2px solid #28a56c;
    border-radius: 18px;
    padding: 22px;
    text-align: center;
    color: #12623e;
}
.result-fake {
    background: #fff0f0;
    border: 2px solid #df5555;
    border-radius: 18px;
    padding: 22px;
    text-align: center;
    color: #a52e2e;
}
.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(110deg,#173c68,#147f91);
    color: white !important;
    border: 0;
    border-radius: 12px;
    min-height: 46px;
    font-weight: 700;
}
.stButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background: #102b4c;
    transform: translateY(-2px);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#e7eef8,#e7f4f4);
}
.footer {
    text-align: center;
    color: #718096;
    padding: 22px;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


# ================= CONNECTION =================

@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )


MODEL_PATH = Path(__file__).parent / "fake_news_model.pkl"

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


try:
    supabase = get_supabase()
    model = load_model()
except Exception as e:
    st.error("Configuration or model loading problem.")
    st.info("Check Supabase Secrets and fake_news_model.pkl.")
    st.exception(e)
    st.stop()


# ================= SESSION =================

if "user" not in st.session_state:
    st.session_state.user = None

if "auth_screen" not in st.session_state:
    st.session_state.auth_screen = "Login"


# ================= HEADER =================

st.markdown("""
<div class="hero">
    <p>ARTIFICIAL INTELLIGENCE • MACHINE LEARNING</p>
    <h1>🔍 TruthLens</h1>
    <p><b>See beyond the headline.</b></p>
    <p>AI-Powered Fake News Detection System</p>
</div>
""", unsafe_allow_html=True)


# ================= LOGIN / SIGNUP =================

if st.session_state.user is None:

    a, b, c = st.columns([1, 1.5, 1])

    with b:

        st.markdown(
            "<h2 style='text-align:center;'>Welcome to TruthLens</h2>",
            unsafe_allow_html=True
        )

        screen = st.radio(
            "Account",
            ["Login", "Create Account"],
            horizontal=True,
            label_visibility="collapsed",
            index=0 if st.session_state.auth_screen == "Login" else 1
        )

        st.session_state.auth_screen = screen

        if screen == "Login":

            st.markdown('<div class="auth-card">', unsafe_allow_html=True)

            st.subheader("🔐 Login to Your Account")

            with st.form("login_form"):

                email = st.text_input("Email Address")
                password = st.text_input("Password", type="password")

                submit = st.form_submit_button(
                    "Login to Dashboard",
                    use_container_width=True
                )

            if submit:

                if not email.strip() or not password:
                    st.warning("Please enter email and password.")

                else:
                    try:
                        response = supabase.auth.sign_in_with_password({
                            "email": email.strip(),
                            "password": password
                        })

                        if response.user:
                            st.session_state.user = response.user
                            st.success("Login successful!")
                            st.rerun()

                    except Exception as e:
                        msg = str(e).lower()

                        if "email not confirmed" in msg:
                            st.warning("Please verify your email first.")
                        elif "invalid login credentials" in msg:
                            st.error("Incorrect email or password.")
                        else:
                            st.error("Login failed. Please try again.")

            st.caption("New user? Select Create Account above.")

            st.markdown("</div>", unsafe_allow_html=True)

        else:

            st.markdown('<div class="auth-card">', unsafe_allow_html=True)

            st.subheader("✨ Create Your Account")

            with st.form("signup_form"):

                new_email = st.text_input("Email Address")
                new_password = st.text_input(
                    "Create Password",
                    type="password"
                )
                confirm = st.text_input(
                    "Confirm Password",
                    type="password"
                )

                submit = st.form_submit_button(
                    "Create My Account",
                    use_container_width=True
                )

            if submit:

                if not new_email.strip() or not new_password or not confirm:
                    st.warning("Please fill in all fields.")

                elif new_password != confirm:
                    st.error("Passwords do not match.")

                elif len(new_password) < 6:
                    st.error("Password must have at least 6 characters.")

                else:
                    try:
                        response = supabase.auth.sign_up({
                            "email": new_email.strip(),
                            "password": new_password
                        })

                        identities = (
                            getattr(response.user, "identities", None)
                            if response.user else None
                        )

                        if identities is not None and len(identities) == 0:
                            st.warning(
                                "Email may already be registered. Please Login."
                            )

                        elif response.session and response.user:
                            st.session_state.user = response.user
                            st.success("Account created!")
                            st.rerun()

                        elif response.user:
                            st.success(
                                "Account created! Check your email for verification."
                            )

                        else:
                            st.warning("Please try again.")

                    except Exception as e:
                        st.error("Signup failed.")
                        st.caption(str(e))

            st.caption("Already registered? Select Login above.")

            st.markdown("</div>", unsafe_allow_html=True)


# ================= MAIN APPLICATION =================

else:

    user = st.session_state.user

    st.sidebar.title("🔍 TruthLens")
    st.sidebar.caption("AI News Intelligence Platform")
    st.sidebar.write("Logged in as:")
    st.sidebar.caption(user.email)

    page = st.sidebar.radio(
        "MAIN MENU",
        ["Dashboard", "Detect News", "Prediction History"]
    )

    if st.sidebar.button("🚪 Logout", use_container_width=True):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        st.session_state.user = None
        st.session_state.auth_screen = "Login"
        st.rerun()


    # ================= DASHBOARD =================

    if page == "Dashboard":

        st.title("🏠 Dashboard")
        st.write("Welcome to your TruthLens dashboard.")

        try:
            response = (
                supabase.table("prediction_history")
                .select("*")
                .eq("user_id", str(user.id))
                .order("created_at", desc=True)
                .execute()
            )

            records = response.data or []

            total = len(records)

            fake = sum(
                1 for x in records
                if x["prediction"] == "FAKE"
            )

            real = sum(
                1 for x in records
                if x["prediction"] == "REAL"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">📰 TOTAL NEWS</div>
                    <div class="stat-value">{total}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">🚨 FAKE NEWS</div>
                    <div class="stat-value">{fake}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-label">✅ REAL NEWS</div>
                    <div class="stat-value">{real}</div>
                </div>
                """, unsafe_allow_html=True)

            st.divider()
            st.subheader("📊 Detection Overview")

            if total > 0:

                chart = pd.DataFrame({
                    "Category": ["FAKE", "REAL"],
                    "Articles": [fake, real]
                }).set_index("Category")

                st.bar_chart(chart)

            else:
                st.info("No news analyzed yet.")

        except Exception as e:
            st.error("Could not load dashboard.")
            st.caption(str(e))


    # ================= NEWS DETECTION =================

    elif page == "Detect News":

        st.title("🔎 Fake News Detection")

        st.write("Enter a news article for AI analysis.")

        with st.container(border=True):

            title = st.text_input(
                "📰 News Headline",
                placeholder="Enter news headline..."
            )

            article = st.text_area(
                "📄 Complete News Article",
                placeholder="Paste complete news article here...",
                height=230
            )

            analyze = st.button(
                "🔍 Analyze News Article",
                use_container_width=True
            )

        if analyze:

            if not title.strip() or not article.strip():

                st.warning("Please enter both headline and article.")

            else:

                try:

                    combined = title.strip() + " " + article.strip()

                    prediction = int(model.predict([combined])[0])

                    probabilities = model.predict_proba([combined])[0]

                    confidence = float(
                        probabilities[prediction]
                    ) * 100

                    result = "REAL" if prediction == 1 else "FAKE"

                    st.divider()
                    st.subheader("Analysis Result")

                    if result == "REAL":

                        st.markdown("""
                        <div class="result-real">
                            <h1>✅ REAL NEWS</h1>
                            <h3>Model classifies this article as REAL.</h3>
                        </div>
                        """, unsafe_allow_html=True)

                    else:

                        st.markdown("""
                        <div class="result-fake">
                            <h1>🚨 FAKE NEWS</h1>
                            <h3>Model classifies this article as FAKE.</h3>
                        </div>
                        """, unsafe_allow_html=True)

                    st.metric(
                        "Model Confidence",
                        f"{confidence:.2f}%"
                    )

                    st.progress(confidence / 100)

                    st.warning(
                        "This is an AI prediction, not a guarantee "
                        "of factual truth. Verify important news "
                        "from reliable sources."
                    )

                    try:

                        supabase.table("prediction_history").insert({
                            "user_id": str(user.id),
                            "news_title": title.strip(),
                            "prediction": result,
                            "confidence": round(confidence, 2)
                        }).execute()

                        st.success("Prediction saved to history.")

                    except Exception as e:
                        st.warning("Prediction completed, but history was not saved.")
                        st.caption(str(e))

                except Exception as e:
                    st.error("Could not analyze article.")
                    st.caption(str(e))


    # ================= HISTORY =================

    elif page == "Prediction History":

        st.title("📚 Prediction History")

        try:

            response = (
                supabase.table("prediction_history")
                .select("*")
                .eq("user_id", str(user.id))
                .order("created_at", desc=True)
                .execute()
            )

            records = response.data or []

            if records:

                df = pd.DataFrame(records)

                df = df.rename(columns={
                    "news_title": "News Title",
                    "prediction": "Prediction",
                    "confidence": "Confidence (%)",
                    "created_at": "Date"
                })

                columns = [
                    "News Title",
                    "Prediction",
                    "Confidence (%)",
                    "Date"
                ]

                st.dataframe(
                    df[columns],
                    use_container_width=True,
                    hide_index=True
                )

                st.download_button(
                    "⬇️ Download History CSV",
                    data=df[columns].to_csv(index=False).encode("utf-8"),
                    file_name="truthlens_history.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            else:
                st.info("No prediction history available yet.")

        except Exception as e:
            st.error("Unable to load history.")
            st.caption(str(e))


# ================= FOOTER =================

st.divider()

st.markdown("""
<div class="footer">
    <b>TruthLens — Fake News Detection System</b><br>
    Introduction to Data Science Project<br>
    Department of Information Technology<br>
    Shaheed Benazir Bhutto University, Shaheed Benazirabad<br>
    Powered by TF-IDF and Logistic Regression
</div>
""", unsafe_allow_html=True)
