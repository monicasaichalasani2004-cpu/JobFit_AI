# JobFit AI 🧠
A simple AI-powered resume + job description matcher that helps you understand fit, find gaps, and improve resume bullets.

## ✨ Features
- Upload resume as **PDF/DOCX** or paste resume text
- Paste **Job Description text**
- Shows a **Job Fit Score**
- Highlights **Matched vs Missing keywords**
- **Bullet Rewriter (ATS-friendly)** (requires OpenAI API key + billing/quota)
- **Tailored Resume Output** (requires OpenAI API key + billing/quota)

> Note: Some AI features require an OpenAI API key with active billing/quota.  
> The basic scoring + skill gap analysis still works without the API.

## 🛠 Tech Stack
- Python
- Streamlit (UI)
- OpenAI API (optional AI features)
- pypdf + python-docx (resume parsing)

## 🚀 Run Locally (Mac / Windows / Linux)

### 1) Create and activate venv
```bash
python3 -m venv venv
source venv/bin/activate
