# 🎓 UniDesk

An AI-powered university portal that brings together a policy Q&A assistant, an AI-generated test prep engine, and a role-based marks & attendance dashboard — all in one Streamlit app.

Built with **Streamlit**, **LangChain**, **LangGraph**, **Groq**, and **ChromaDB**.

---

## ✨ Features

### 🏫 University Information Assistant
A RAG-powered chatbot that answers questions about university policies — attendance rules, exam patterns, internal marks calculation, fees, and more — by retrieving answers directly from official university PDFs, with page-number source citations.

### 📝 Test Prep Engine
Upload a syllabus PDF and generate custom multiple-choice practice questions using an AI agent pipeline. Choose difficulty (Easy / Medium / Hard) and number of questions, attempt the quiz, get instant scoring, and see explanations for each answer.

### 📊 Marks & Attendance Dashboard
Role-based academic dashboard:
- **Admins** see the full class list, class averages, top performers, and students with low attendance.
- **Students** see their own subject-wise marks, attendance percentage, and class rank.

### 🔐 Authentication
Login system with per-user sessions (via `streamlit-authenticator`), separating admin and student views.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI / App Framework | Streamlit |
| Authentication | streamlit-authenticator |
| LLM Orchestration | LangChain, LangGraph |
| LLM Provider | Groq |
| Vector Store | ChromaDB |
| PDF Parsing | PyMuPDF (fitz) |
| Data Handling | pandas, openpyxl |
| Storage | SQLite (chat history) |

---
## 📌 System Architecture

```
                         User Login
                             │
                             ▼
                   Authentication System
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
 University Q&A        Test Prep Engine      Marks Dashboard
   (RAG Chatbot)        (Agent Pipeline)      (Role-Based)
        │                    │                    │
        ▼                    ▼                    ▼
  Chroma Vector DB      Syllabus PDF Text      SQLite Database
   (Policy PDFs)         (PyMuPDF Extract)      (Marks/Attendance)
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ▼
                   Groq LLM (via LangChain / LangGraph)
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
  Cited Answers        Generated MCQs        Analytics & Insights
                             │
                             ▼
                  Interactive Streamlit Dashboard
```

---

## 📂 Project Structure

```
UniDesk/
├── app.py                     # Main Streamlit app (UI + routing)
├── requirements.txt
├── src/
│   ├── database.py             # SQLite chat history logic
│   ├── ingest.py                # Syllabus PDF ingestion
│   ├── ingest_gitam.py           # University regulations PDF ingestion
│   ├── retriever.py              # Vector store retriever
│   ├── gitam_retriever.py        # Retriever for university regulations
│   ├── mcq_agent.py              # AI agent pipeline for MCQ generation
│   ├── marks.py                  # Marks & attendance queries
│   └── university_qa.py          # RAG Q&A logic
├── data/
│   ├── pdfs/                     # Syllabus PDFs (gitignored)
│   ├── university_pdfs/          # University regulations PDF (gitignored)
│   └── students.xlsx             # Student marks/attendance (gitignored)
└── vectorstore/                # ChromaDB persisted vectors (gitignored)
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Sindhuja0206/UniDesk.git
cd UniDesk
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Add your data
- Place syllabus PDFs in `data/pdfs/`
- Place the university regulations PDF at `data/university_pdfs/gitam.pdf`
- Place a student marks spreadsheet at `data/students.xlsx`

### 5. Run the app
```bash
streamlit run app.py
```
The app will open at `http://localhost:8501`.

