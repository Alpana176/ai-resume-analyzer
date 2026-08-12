import streamlit as st
import plotly.graph_objects as go
import tempfile
import os
import sys


# =========================================================
# PROJECT PATH
# =========================================================

sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# =========================================================
# IMPORT PROJECT MODULES
# =========================================================

from chatbot.bot import GeminiChatbot
from services.resume_loader import extract_text_from_pdf
from services.text_splitter import split_text
from services.vector_store import (
    create_vector_store,
    retrieve_chunks
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <h1 style='text-align: center;'>
        📄 AI Resume Analyzer
    </h1>

    <p style='text-align: center; color: gray;'>
        RAG-powered resume analysis using Gemini AI
    </p>

    <hr>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD GEMINI BOT ONCE
# =========================================================

@st.cache_resource
def load_bot():
    return GeminiChatbot()


try:
    bot = load_bot()

except Exception as e:
    st.error("❌ Could not initialize Gemini AI.")
    st.exception(e)
    st.stop()


# =========================================================
# MATCH SCORE GAUGE
# =========================================================

def render_gauge(score):

    try:
        score = int(score)

    except (TypeError, ValueError):
        score = 0

    score = max(
        0,
        min(100, score)
    )

    if score >= 80:
        label = "Strong Match 💪"

    elif score >= 60:
        label = "Moderate Match 👍"

    elif score >= 40:
        label = "Weak Match ⚠️"

    else:
        label = "Poor Match ❌"


    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",

            value=score,

            title={
                "text": f"Match Score — {label}",
                "font": {
                    "size": 18
                }
            },

            gauge={
                "axis": {
                    "range": [0, 100]
                },

                "bar": {
                    "color": "#4F8BF9"
                },

                "steps": [
                    {
                        "range": [0, 40],
                        "color": "#fde8e8"
                    },
                    {
                        "range": [40, 60],
                        "color": "#fef3cd"
                    },
                    {
                        "range": [60, 80],
                        "color": "#fff3cd"
                    },
                    {
                        "range": [80, 100],
                        "color": "#d4edda"
                    }
                ],

                "threshold": {
                    "line": {
                        "color": "#4F8BF9",
                        "width": 4
                    },

                    "thickness": 0.75,

                    "value": score
                }
            }
        )
    )


    fig.update_layout(
        height=300,
        margin=dict(
            t=40,
            b=0,
            l=20,
            r=20
        )
    )


    st.plotly_chart(
        fig,
        width="stretch"
    )


# =========================================================
# HELPER FUNCTION
# =========================================================
# Your retrieve_chunks() may return:
#
# 1. ["chunk 1", "chunk 2"]
#
# OR
#
# 2. [{"text": "chunk 1", "score": 0.8}, ...]
#
# This function supports BOTH formats.
# =========================================================

def normalize_chunks(relevant_chunks):

    normalized = []

    if not relevant_chunks:
        return normalized


    for item in relevant_chunks:

        # ---------------------------------------------
        # Case 1: chunk is already a string
        # ---------------------------------------------

        if isinstance(item, str):

            if item.strip():
                normalized.append(item.strip())

            continue


        # ---------------------------------------------
        # Case 2: chunk is a dictionary
        # ---------------------------------------------

        if isinstance(item, dict):

            text = item.get("text")

            if text and isinstance(text, str):

                normalized.append(
                    text.strip()
                )

            continue


    return normalized


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📄 AI Resume Analyzer")

    st.caption(
        "RAG-powered resume analysis for job matching"
    )

    st.markdown("---")

    job_role = st.text_input(
        "🎯 Target Job Role",
        placeholder="e.g. Generative AI Engineer"
    )

    job_description = st.text_area(
        "📋 Job Description",
        placeholder="Paste the complete job description here...",
        height=220
    )

    uploaded_file = st.file_uploader(
        "📤 Upload Resume PDF",
        type=["pdf"]
    )

    analyze_btn = st.button(
        "🚀 Analyze Resume",
        width="stretch"
    )


# =========================================================
# MAIN ANALYSIS
# =========================================================

if analyze_btn:

    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    if not job_role.strip():

        st.warning(
            "⚠️ Please enter a target job role."
        )

        st.stop()


    if not job_description.strip():

        st.warning(
            "⚠️ Please paste the job description."
        )

        st.stop()


    if uploaded_file is None:

        st.warning(
            "⚠️ Please upload your resume PDF."
        )

        st.stop()


    # =====================================================
    # ANALYSIS
    # =====================================================

    with st.spinner(
        "🔍 Extracting, retrieving and "
        "analyzing your resume..."
    ):

        tmp_path = None


        try:

            # =================================================
            # STEP 1 — SAVE PDF TEMPORARILY
            # =================================================

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:

                tmp.write(
                    uploaded_file.getvalue()
                )

                tmp_path = tmp.name


            # =================================================
            # STEP 2 — PDF TEXT EXTRACTION
            # =================================================

            st.info(
                "📄 Extracting resume text..."
            )


            resume_text = extract_text_from_pdf(
                tmp_path
            )


            if (
                not resume_text
                or resume_text.startswith("ERROR")
                or not resume_text.strip()
            ):

                st.error(
                    "❌ Could not extract text "
                    "from this PDF."
                )

                st.info(
                    "Please upload a text-based PDF. "
                    "Scanned/image-only resumes may "
                    "require OCR."
                )

                st.stop()


            # Show small extraction preview
            with st.expander(
                "📄 View Extracted Resume Text"
            ):

                st.text(
                    resume_text[:5000]
                )


            # =================================================
            # STEP 3 — TEXT CHUNKING
            # =================================================

            chunks = split_text(
                resume_text
            )


            if not chunks:

                st.error(
                    "❌ No meaningful resume chunks "
                    "were created."
                )

                st.stop()


            st.success(
                f"✅ Resume processed into "
                f"{len(chunks)} text chunks."
            )


            # =================================================
            # STEP 4 — CREATE VECTOR STORE
            # =================================================

            index, embeddings, chunks = (
                create_vector_store(
                    chunks
                )
            )


            # =================================================
            # STEP 5 — JOB-AWARE RETRIEVAL
            # =================================================

            query = f"""
TARGET JOB ROLE:
{job_role}

JOB DESCRIPTION:
{job_description}

Find the most relevant sections of the candidate's
resume for evaluating their suitability for this role.

Prioritize:

- Technical skills
- Programming languages
- Frameworks
- Libraries
- AI / ML / Generative AI
- LLMs
- RAG
- Vector databases
- Projects
- Work experience
- Education
- Certifications
- Achievements
- Role-specific qualifications
"""


            # -------------------------------------------------
            # Retrieve relevant resume chunks
            # -------------------------------------------------

            try:

                relevant_chunks = retrieve_chunks(
                    query=query,
                    index=index,
                    chunks=chunks,
                    top_k=5
                )

            except TypeError:

                # Fallback if retrieve_chunks()
                # does not support top_k

                relevant_chunks = retrieve_chunks(
                    query,
                    index,
                    chunks
                )


            if not relevant_chunks:

                st.error(
                    "❌ Could not retrieve relevant "
                    "resume information."
                )

                st.stop()


            # =================================================
            # STEP 6 — NORMALIZE RETRIEVED CHUNKS
            # =================================================

            relevant_chunks = normalize_chunks(
                relevant_chunks
            )


            if not relevant_chunks:

                st.error(
                    "❌ Retrieved resume chunks "
                    "contained no readable text."
                )

                st.stop()


            # =================================================
            # STEP 7 — BUILD LLM CONTEXT
            # =================================================

            context = "\n\n".join(
                relevant_chunks
            )


            # =================================================
            # STEP 8 — GEMINI ANALYSIS
            # =================================================

            st.info(
                "🤖 Gemini is analyzing your resume "
                "against the job description..."
            )


            response = bot.get_response(
                context=context,
                job_role=job_role,
                job_description=job_description
            )


            # =================================================
            # STEP 9 — HANDLE GEMINI ERRORS
            # =================================================

            if not response:

                st.error(
                    "❌ Gemini returned an empty response."
                )

                st.stop()


            if "error" in response:

                st.error(
                    "❌ Analysis failed: "
                    + str(
                        response["error"]
                    )
                )


                # Show raw response if available
                if response.get("raw"):

                    with st.expander(
                        "🔎 View Gemini Raw Response"
                    ):

                        st.code(
                            response["raw"]
                        )

                st.stop()


            # =================================================
            # STEP 10 — EXTRACT RESPONSE
            # =================================================

            score = response.get(
                "match_score",
                0
            )


            strengths = response.get(
                "strengths",
                []
            )


            missing = response.get(
                "missing_skills",
                []
            )


            weaknesses = response.get(
                "weaknesses",
                []
            )


            suggestions = response.get(
                "suggestions",
                []
            )


            # Make sure response lists are actually lists

            if not isinstance(
                strengths,
                list
            ):
                strengths = [str(strengths)]


            if not isinstance(
                missing,
                list
            ):
                missing = [str(missing)]


            if not isinstance(
                weaknesses,
                list
            ):
                weaknesses = [str(weaknesses)]


            if not isinstance(
                suggestions,
                list
            ):
                suggestions = [str(suggestions)]


            # =================================================
            # STEP 11 — MATCH SCORE
            # =================================================

            st.markdown(
                "## 🎯 Resume–Job Match"
            )


            render_gauge(
                score
            )


            # =================================================
            # STEP 12 — ANALYSIS SUMMARY
            # =================================================

            st.markdown("---")


            st.markdown(
                "## 📊 Analysis Summary"
            )


            col1, col2 = st.columns(2)


            # =================================================
            # STRENGTHS + WEAKNESSES
            # =================================================

            with col1:

                st.markdown(
                    "### ✅ Strengths"
                )


                if strengths:

                    for strength in strengths:

                        st.success(
                            str(strength)
                        )

                else:

                    st.info(
                        "No major strengths identified."
                    )


                st.markdown(
                    "### ⚠️ Weaknesses"
                )


                if weaknesses:

                    for weakness in weaknesses:

                        st.warning(
                            str(weakness)
                        )

                else:

                    st.info(
                        "No major weaknesses identified."
                    )


            # =================================================
            # MISSING SKILLS + SUGGESTIONS
            # =================================================

            with col2:

                st.markdown(
                    "### ❌ Missing Skills"
                )


                if missing:

                    for skill in missing:

                        st.error(
                            str(skill)
                        )

                else:

                    st.success(
                        "No major missing skills identified."
                    )


                st.markdown(
                    "### 💡 Improvement Suggestions"
                )


                if suggestions:

                    for suggestion in suggestions:

                        st.info(
                            str(suggestion)
                        )

                else:

                    st.info(
                        "No suggestions available."
                    )


            # =================================================
            # STEP 13 — RETRIEVED CONTEXT
            # =================================================

            st.markdown("---")


            with st.expander(
                "🔎 View Retrieved Resume Context"
            ):

                st.caption(
                    "These resume sections were selected "
                    "using semantic similarity before "
                    "being provided to Gemini."
                )


                for i, chunk in enumerate(
                    relevant_chunks,
                    start=1
                ):

                    st.markdown(
                        f"### 📌 Retrieved Chunk {i}"
                    )


                    st.write(
                        chunk
                    )


                    st.divider()


            # =================================================
            # STEP 14 — RAG PIPELINE
            # =================================================

            with st.expander(
                "⚙️ View Technical RAG Pipeline"
            ):

                st.markdown(
                    """
                    ### RAG Architecture

                    **1. Resume PDF**

                    ↓

                    **2. PDF Text Extraction**

                    ↓

                    **3. Overlapping Text Chunking**

                    ↓

                    **4. Sentence Transformer Embeddings**

                    `all-MiniLM-L6-v2`

                    ↓

                    **5. FAISS Vector Index**

                    ↓

                    **6. Job Description-Aware Semantic Retrieval**

                    ↓

                    **7. Top-K Relevant Resume Chunks**

                    ↓

                    **8. Gemini LLM**

                    ↓

                    **9. Structured JSON Response**

                    ↓

                    **10. Streamlit Dashboard**
                    """
                )


            # =================================================
            # STEP 15 — ANALYSIS METRICS
            # =================================================

            st.markdown("---")


            st.markdown(
                "### 📈 Processing Details"
            )


            metric1, metric2, metric3 = (
                st.columns(3)
            )


            with metric1:

                st.metric(
                    "Resume Chunks",
                    len(chunks)
                )


            with metric2:

                st.metric(
                    "Retrieved Chunks",
                    len(relevant_chunks)
                )


            with metric3:

                st.metric(
                    "Match Score",
                    f"{score}/100"
                )


        # =================================================
        # GENERAL ERROR HANDLING
        # =================================================

        except Exception as e:

            st.error(
                "❌ Unexpected error occurred."
            )

            st.exception(
                e
            )


        # =================================================
        # CLEAN TEMPORARY FILE
        # =================================================

        finally:

            if (
                tmp_path
                and os.path.exists(tmp_path)
            ):

                try:

                    os.remove(
                        tmp_path
                    )

                except OSError:

                    pass


# =========================================================
# EMPTY STATE
# =========================================================

else:

    st.markdown(
        """
        <div style='text-align: center; padding: 40px;'>

        <h2>👋 Welcome to AI Resume Analyzer</h2>

        <p>
        Analyze your resume against any job description
        using Retrieval-Augmented Generation (RAG).
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown("---")


    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            "### 🎯 Match Score"
        )

        st.caption(
            "Get a 0–100 compatibility score "
            "between your resume and the target role."
        )


    with col2:

        st.markdown(
            "### 🔎 Missing Skills"
        )

        st.caption(
            "Identify important skills mentioned "
            "in the job description but missing "
            "from your resume."
        )


    with col3:

        st.markdown(
            "### 💡 AI Suggestions"
        )

        st.caption(
            "Receive actionable recommendations "
            "to improve your resume for the role."
        )


    st.markdown("---")


    st.info(
        "👈 Enter the Target Job Role, paste the Job "
        "Description, upload your Resume PDF and click "
        "**🚀 Analyze Resume**."
    )


    st.markdown(
        """
        ### ⚙️ How it works

        **Resume PDF**
        → Text Extraction
        → Text Chunking
        → Sentence Transformer Embeddings
        → FAISS Semantic Search
        → Job-Aware Retrieval
        → Gemini AI
        → Structured Resume Analysis
        """
    )