## 🎓 Overview

UniDesk is an **AI-powered university portal** that streamlines academic support and campus administration through a unified platform. It integrates a **Retrieval-Augmented Generation (RAG)**-based university policy assistant, an **AI-driven test preparation engine**, and a **secure role-based academic dashboard** into a single Streamlit application.

Built with **Streamlit, LangChain, LangGraph, Groq, ChromaDB, SQLite, and PyMuPDF**, UniDesk leverages **RAG** and **AI agent workflows** to deliver accurate, source-cited answers from official university documents, generate personalized MCQs from syllabus PDFs, and provide role-based access to marks, attendance, rankings, and academic insights.

### ✨ Key Highlights

- 🤖 **RAG-powered University Assistant** with source-cited responses from official university documents.
- 📝 **AI Test Preparation Engine** that generates customizable MCQs with explanations from uploaded syllabus PDFs.
- 📊 **Role-Based Academic Dashboard** for managing marks, attendance, rankings, and class analytics.
- 🔐 **Secure Authentication** with dedicated student and administrator portals.
- ⚡ **Modern AI Stack** powered by Streamlit, LangChain, LangGraph, Groq, ChromaDB, SQLite, and PyMuPDF.

UniDesk showcases the practical application of **Generative AI**, **Retrieval-Augmented Generation (RAG)**, **AI agent workflows**, and **vector databases** to build an intelligent, end-to-end academic management solution.

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

---

## 🌍 Use Cases

- Universities & Colleges
- Learning Management Systems (LMS)
- Coaching Institutes / Test Prep Centers
- Students
- Faculty & Academic Advisors

---

## 🚀 Deployment

UniDesk can be deployed on:
-  Streamlit Community Cloud
-  Railway
-  Render
-  Hugging Face Spaces
-  Docker

---
