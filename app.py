import streamlit as st
import re
from collections import Counter
from io import BytesIO
from openai import OpenAI

# Optional libs for parsing
from pypdf import PdfReader
import docx

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="JobFit AI", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1.2rem; }
.small { color: #9ca3af; font-size: 0.9rem; }
.card {
  padding: 16px;
  border: 1px solid rgba(120,120,120,0.25);
  border-radius: 14px;
  background: rgba(255,255,255,0.03);
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("# 🧠 JobFit AI")
st.markdown("### Make your resume fit the job.")
st.markdown("<div class='small'>Upload your resume (PDF/DOCX) or paste text + job description → get score, gaps, and next steps.</div>", unsafe_allow_html=True)
st.divider()

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("🔐 API Key (optional)")
    api_key = st.text_input("OpenAI API key", type="password")
    st.caption("If billing/quota isn't active, the app still works (score + skills).")
    st.markdown("---")
    st.subheader("⚙️ Output Style")
    tone = st.selectbox("Tone", ["Professional", "Confident", "Simple"])
    detail = st.selectbox("Detail", ["Short", "Medium", "Detailed"])

# ---------- HELPERS ----------
def clean_text(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9 ]", " ", text.lower())

def extract_keywords(text: str) -> Counter:
    words = clean_text(text).split()
    stop = set([
        "and","or","the","a","an","to","for","with","of","in","on","is","are",
        "as","at","by","from","this","that","be","will","you","we","our"
    ])
    keywords = [w for w in words if w not in stop and len(w) > 2]
    return Counter(keywords)

def fit_label(score: int) -> str:
    if score >= 80:
        return "Strong match ✅"
    if score >= 60:
        return "Good match (needs improvement) 👍"
    return "Low match (needs fixes) ⚠️"

def read_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text).strip()

def read_docx(file_bytes: bytes) -> str:
    f = BytesIO(file_bytes)
    d = docx.Document(f)
    return "\n".join([p.text for p in d.paragraphs]).strip()

# ---------- INPUTS ----------
left, right = st.columns(2)

with left:
    st.markdown("#### 📄 Resume")

    upload = st.file_uploader("Upload resume (PDF or DOCX)", type=["pdf", "docx"])
    resume_text = ""

    if upload is not None:
        file_bytes = upload.read()
        if upload.name.lower().endswith(".pdf"):
            resume_text = read_pdf(file_bytes)
        elif upload.name.lower().endswith(".docx"):
            resume_text = read_docx(file_bytes)

        st.success(f"Uploaded: {upload.name}")
        st.text_area("Extracted resume text (editable)", value=resume_text, height=220, key="resume_extracted")
        resume_text = st.session_state["resume_extracted"]
    else:
        resume_text = st.text_area("Or paste resume text", height=300, placeholder="Paste your resume here...")

with right:
    st.markdown("#### 🧾 Job Description")
    job_text = st.text_area("Paste job description", height=300, placeholder="Paste the job description here...")

# ---------- ACTION ----------
if st.button("🚀 Analyze", use_container_width=True):

    if not resume_text or not job_text:
        st.error("Please upload/paste resume AND paste job description.")
    else:
        with st.spinner("Analyzing..."):
            resume_kw = extract_keywords(resume_text)
            job_kw = extract_keywords(job_text)

            matched = set(resume_kw.keys()) & set(job_kw.keys())
            missing = set(job_kw.keys()) - set(resume_kw.keys())
            score = int((len(matched) / max(len(job_kw), 1)) * 100)

        st.divider()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Job Fit Score", f"{score}%")
        c2.metric("Matched Skills", len(matched))
        c3.metric("Missing Skills", len(missing))
        c4.markdown(f"<div class='card'><b>Status</b><br>{fit_label(score)}</div>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📌 Overview", "🧩 Skills", "🧠 AI Feedback"])

        with tab1:
            st.markdown(
                "<div class='card'>"
                "<b>What this means</b><br>"
                "This score is based on keyword overlap. Improve by adding relevant skills and rewriting bullets with impact."
                "</div>",
                unsafe_allow_html=True
            )

        with tab2:
            colA, colB = st.columns(2)
            with colA:
                st.markdown("#### ✅ Matched Skills (top 25)")
                if matched:
                    for s in list(matched)[:25]:
                        st.write("•", s)
                else:
                    st.info("No strong matches detected yet.")
            with colB:
                st.markdown("#### ❌ Missing Skills (top 25)")
                if missing:
                    for s in list(missing)[:25]:
                        st.write("•", s)
                else:
                    st.success("Great! No major keyword gaps found.")

        with tab3:
            if not api_key:
                st.warning("AI feedback is off because no API key was provided.")
                st.info("✅ You can still use score + skills. Add an API key (with active billing/quota) to enable AI feedback.")
            else:
                prompt = f"""
You are JobFit AI — an honest career assistant.

Rules:
- Do NOT invent experience.
- Give actionable, specific feedback.
- Tone: {tone}
- Detail level: {detail}

Tasks:
1) Explain why the resume matches or doesn't match this job.
2) List TOP missing skills/keywords (only if relevant).
3) Suggest 3 resume improvements (content + structure).
4) Rewrite 2 bullet points ATS-friendly using ONLY existing information.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_text}
"""
                try:
                    client = OpenAI(api_key=api_key)
                    with st.spinner("Generating AI feedback..."):
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "You help users improve resumes honestly and clearly."},
                                {"role": "user", "content": prompt}
                            ],
                        )
                    result = response.choices[0].message.content
                    st.markdown(
                        "<div class='card'><b>AI Feedback</b><br><br>"
                        + result.replace("\n", "<br>")
                        + "</div>",
                        unsafe_allow_html=True
                    )
                except Exception:
                    st.warning("AI feedback unavailable (API billing/quota issue).")
                    st.info("✅ Score + skills still work. Enable billing/quota on your OpenAI Platform account.")
