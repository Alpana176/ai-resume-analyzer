import streamlit as st
import plotly.graph_objects as go
import tempfile
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot.bot import GeminiChatbot
from services.resume_loader import extract_text_from_pdf
from services.text_splitter import split_text
from services.vector_store import create_vector_store, retrieve_chunks

# ✅ Page config
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ✅ Header
st.markdown("""
    <h1 style='text-align: center; color: #4F8BF9;'>📄 AI Resume Analyzer</h1>
    <p style='text-align: center; color: gray;'>ATS-style resume analysis powered by Gemini AI</p>
    <hr>
""", unsafe_allow_html=True)

# ✅ Initialize bot once
@st.cache_resource
def load_bot():
    return GeminiChatbot()

bot = load_bot()

# ✅ Gauge chart function
def render_gauge(score):
    if score >= 80:
        color = "#2ecc71"
        label = "Strong Match 💪"
    elif score >= 60:
        color = "#f39c12"
        label = "Moderate Match 👍"
    elif score >= 40:
        color = "#e67e22"
        label = "Weak Match ⚠️"
    else:
        color = "#e74c3c"
        label = "Poor Match ❌"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": f"Match Score — {label}", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0, 40], "color": "#fde8e8"},
                {"range": [40, 60], "color": "#fef3cd"},
                {"range": [60, 80], "color": "#fff3cd"},
                {"range": [80, 100], "color": "#d4edda"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": score
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(t=40, b=0, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

# ✅ Sidebar input
with st.sidebar:
    st.header("📋 Input Details")
    job_role = st.text_input("🎯 Target Job Role", placeholder="e.g. Python Developer")
    uploaded_file = st.file_uploader("📤 Upload Resume PDF", type=["pdf"])
    analyze_btn = st.button("🚀 Analyze Resume", use_container_width=True)
    st.markdown("---")
    st.caption("Built with Gemini AI + RAG + FAISS")

# ✅ Main area
if analyze_btn:
    if not job_role:
        st.warning("⚠️ Please enter a job role.")
    elif uploaded_file is None:
        st.warning("⚠️ Please upload a resume PDF.")
    else:
        with st.spinner("🔍 Analyzing your resume..."):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name


            try:
                # ✅ RAG Pipeline
                resume_text = extract_text_from_pdf(tmp_path)

                if resume_text.startswith("ERROR") or resume_text.strip() == "":
                    st.error("❌ Could not extract text from PDF. Try another file.")
                else:
                    chunks = split_text(resume_text)
                    index, embeddings, chunks = create_vector_store(chunks)
                    query = "Analyze this resume for weaknesses and suggestions"
                    relevant_chunks = retrieve_chunks(query, index, chunks)
                    context = "\n\n".join(relevant_chunks)

                    response = bot.get_response(context, job_role)

                    if "error" in response:
                        st.error("❌ Error: " + response["error"])
                    else:
                        score = response.get("match_score", 0)
                        strengths = response.get("strengths", [])
                        missing = response.get("missing_skills", [])
                        weaknesses = response.get("weaknesses", [])
                        suggestions = response.get("suggestions", [])

                        # ✅ Gauge chart
                        st.markdown("### 🎯 Match Score")
                        render_gauge(score)

                        st.markdown("---")

                        # ✅ 2 column layout
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("### ✅ Strengths")
                            if strengths:
                                for s in strengths:
                                    st.success(s)
                            else:
                                st.info("No strengths identified.")

                            st.markdown("### ⚠️ Weaknesses")
                            if weaknesses:
                                for w in weaknesses:
                                    st.warning(w)
                            else:
                                st.info("No weaknesses identified.")

                        with col2:
                            st.markdown("### ❌ Missing Skills")
                            if missing:
                                for m in missing:
                                    st.error(m)
                            else:
                                st.info("No missing skills identified.")

                            st.markdown("### 💡 Suggestions")
                            if suggestions:
                                for sug in suggestions:
                                    st.info(sug)
                            else:
                                st.info("No suggestions available.")

            finally:
                os.remove(tmp_path)

else:
    # ✅ Empty state
    st.markdown("""
        <div style='text-align: center; padding: 60px; color: gray;'>
            <h3>👈 Upload your resume and enter a job role to get started</h3>
            <p>You'll get a full ATS-style analysis with match score, strengths, missing skills and suggestions.</p>
        </div>
    """, unsafe_allow_html=True)