import streamlit as st
import streamlit_authenticator as stauth
from src.ingest import ingest_all_pdfs
from src.ingest_gitam import ingest_gitam_pdf
from src.mcq_agent import generate_mcqs_with_agents
from src.university_qa import ask_university
from src.database import init_db, save_chat
from src.marks import (
    load_excel_to_db, get_all_students, get_student_by_roll, get_student_by_name,
    get_class_summary, get_top_students, get_low_attendance_students, get_student_rank
)
from src.theme import inject_theme, get_header_banner
import os
import fitz

# Initialize database
init_db()

st.set_page_config(
    page_title="UniDesk",
    page_icon="🎓",
    layout="wide"
)

# Inject custom visual theme stylesheet
def inject_cats_theme():
    css_path = os.path.join(os.path.dirname(__file__), "assets/style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        inject_theme()

inject_cats_theme()

# ─── AUTH ───
credentials = {
    "usernames": {
        "admin":     {"name": "Admin",     "password": stauth.utilities.hasher.Hasher.hash("admin123")},
        "nikhita":     {"name": "Nikhita",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "navya":     {"name": "Navya",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "sindhuja":     {"name": "Sindhuja",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "srihita":     {"name": "Srihita",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "srushti":     {"name": "Srushti",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "karthi":     {"name": "Karthi",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "gnaneswar":     {"name": "Gnaneswar",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "varshini":     {"name": "Varshini",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "mokshagna":     {"name": "Mokshagna",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "mounika":     {"name": "Mounika",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "nayana":     {"name": "Nayana",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "choshik":     {"name": "Choshik",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "shwetha":     {"name": "Shwetha",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "siri":     {"name": "Siri",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
        "bhargav":     {"name": "Bhargav",     "password": stauth.utilities.hasher.Hasher.hash("student123")},
    }
}
authenticator = stauth.Authenticate(credentials, "university_rag", "abcdef", cookie_expiry_days=1)
authenticator.login(location="main")
name = st.session_state.get("name")
username = st.session_state.get("username")
authentication_status = st.session_state.get("authentication_status")

if authentication_status is False:
    st.error("❌ Incorrect username or password")
    st.stop()
elif authentication_status is None:
    st.warning("Please enter your username and password")
    st.stop()

# ─── MAIN APP ───
role = "Administrator" if username == "admin" else "Student"
top_bar_html = f"""
<div class="cats-top-bar">
    <div class="cats-top-bar-left">
        <span class="cats-logo">🎓</span>
        <span class="cats-app-name">UniDesk</span>
    </div>
    <div class="cats-top-bar-right">
        <span class="cats-session-badge">Academic Session: 2026-27</span>
    </div>
</div>
<div style="margin-bottom: 20px; padding: 0 4px;">
    <h1 style="margin: 0; color: #1f2937; font-size: 1.8rem; font-weight: 700;">Academic Track</h1>
    <p style="margin: 4px 0 0 0; color: #6b7280; font-size: 0.95rem;">
        Welcome back, <span style="color: #0d5c4f; font-weight: 700;">{name}</span> | Role: <strong>{role}</strong>
    </p>
</div>
"""
st.markdown(top_bar_html, unsafe_allow_html=True)

# Helper function for notice banners in CATS style
def render_notice(text, is_warning=False):
    icon = "⚠️" if is_warning else "ℹ️"
    return f"""
    <div class="cats-notice-banner">
        <div class="cats-notice-icon">{icon}</div>
        <div class="cats-notice-content">{text}</div>
    </div>
    """

# Helper function to render styled HTML tables
def to_html_table(df, is_marks_table=False):
    import pandas as pd
    df_temp = df.copy()
    has_summary = False
    if is_marks_table and not df_temp.empty:
        for col in ["ANN", "OOSE", "Deep Learning", "Total", "Average", "Attendance (%)"]:
            if col in df_temp.columns:
                df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce')
        
        avg_ann = round(df_temp["ANN"].mean(), 2)
        avg_oose = round(df_temp["OOSE"].mean(), 2)
        avg_dl = round(df_temp["Deep Learning"].mean(), 2)
        avg_total = round(df_temp["Total"].mean(), 2)
        avg_avg = round(df_temp["Average"].mean(), 2)
        avg_att = round(df_temp["Attendance (%)"].mean(), 2)
        
        summary_row = {
            "Roll No": "",
            "Name": "Class Average",
            "ANN": avg_ann,
            "OOSE": avg_oose,
            "Deep Learning": avg_dl,
            "Total": avg_total,
            "Average": avg_avg,
            "Attendance (%)": f"{avg_att}%",
            "Status": ""
        }
        df_temp = pd.concat([df_temp, pd.DataFrame([summary_row])], ignore_index=True)
        has_summary = True
    
    if not is_marks_table:
        if "Attendance (%)" in df_temp.columns:
            df_temp["Attendance (%)"] = df_temp["Attendance (%)"].apply(lambda x: f"{x}%" if isinstance(x, (int, float)) else x)
            
    html = df_temp.to_html(index=False, escape=False, classes="cats-table")
    
    if has_summary:
        parts = html.rsplit('<tr>', 1)
        if len(parts) == 2:
            html = parts[0] + '<tr class="summary-row">' + parts[1]
            
    return f'<div class="table-container">{html}</div>'

# ─── SIDEBAR ───
with st.sidebar:
    role = "Administrator" if username == "admin" else "Student"
    user_card_html = f"""
    <div class="cats-user-card">
        <div class="cats-avatar">👤</div>
        <div class="cats-user-name">{name}</div>
        <div class="cats-user-role">{role} (ID: {username})</div>
    </div>
    """
    st.markdown(user_card_html, unsafe_allow_html=True)
    authenticator.logout("🚪 Logout", "sidebar")
    st.divider()
    
    # Syllabus PDF upload
    st.markdown('<div class="sidebar-section-title">📚 Syllabus PDF Panel</div>', unsafe_allow_html=True)
    syllabus_file = st.file_uploader(
        "Upload syllabus PDF",
        type=["pdf"],
        key="syllabus_upload",
        label_visibility="collapsed"
    )
    if syllabus_file:
        save_path = os.path.join("data/pdfs", syllabus_file.name)
        with open(save_path, "wb") as f:
            f.write(syllabus_file.getbuffer())
        if st.button("⚡ Ingest Syllabus", use_container_width=True):
            with st.spinner("Ingesting..."):
                ingest_all_pdfs()
            st.success("✅ Syllabus ingested!")
            st.session_state["syllabus_path"] = save_path

    # GITAM Regulations PDF management (admin only)
    if username == "admin":
        st.divider()
        st.markdown('<div class="sidebar-section-title">🏫 GITAM Academic Regulations</div>', unsafe_allow_html=True)
        GITAM_PDF_PATH = "data/university_pdfs/gitam.pdf"
        if os.path.exists(GITAM_PDF_PATH):
            st.caption("✅ GITAM PDF found on server")
        else:
            st.caption("⚠️ GITAM PDF not found at data/university_pdfs/gitam.pdf")

        if st.button("⚡ (Re)Ingest GITAM PDF", use_container_width=True):
            with st.spinner("Ingesting GITAM regulations..."):
                msg = ingest_gitam_pdf(GITAM_PDF_PATH)
            st.success(msg) if msg.startswith("✅") else st.error(msg)

# ─── TABS ───
if username == "admin":
    tab1, tab2, tab3 = st.tabs(["🏫 Ask any questions", "📝 Test Prep Engine", "📊 Student Marks (Admin)"])
else:
    tab1, tab2, tab3 = st.tabs(["🏫 Ask any questions", "📝 Test Prep Engine", "📊 My Marks"])

# ══════════════════════════════════════════
# TAB 1 — UNIVERSITY Q&A
# ══════════════════════════════════════════
with tab1:
    with st.container(border=True):
        st.subheader("🏫 University Information Assistant")
        st.caption("Ask about attendance, exams, rules, fees and more!")

        # Always-visible PDF download button
        gitam_pdf_path = "data/university_pdfs/gitam.pdf"
        if os.path.exists(gitam_pdf_path):
            with open(gitam_pdf_path, "rb") as f:
                st.download_button(
                    "📄 Download GITAM Academic Regulations PDF",
                    data=f,
                    file_name="GITAM_Academic_Regulations.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        # Sample questions
        st.markdown("**💡 Try asking:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Attendance criteria?", use_container_width=True):
                st.session_state["uni_question"] = "What is the attendance criteria?"
        with col2:
            if st.button("📝 Exam pattern?", use_container_width=True):
                st.session_state["uni_question"] = "What is the exam pattern?"
        with col3:
            if st.button("📊 Internal marks?", use_container_width=True):
                st.session_state["uni_question"] = "How are internal marks calculated?"

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Chat history
    if "uni_messages" not in st.session_state:
        st.session_state.uni_messages = []

    for message in st.session_state.uni_messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Pre-filled question from buttons
    default_q = st.session_state.pop("uni_question", "")

    if prompt := st.chat_input("Ask about university rules, attendance, exams...", key="uni_input"):
        default_q = prompt

    if default_q:
        st.session_state.uni_messages.append({"role": "user", "content": default_q})
        with st.chat_message("user", avatar="👤"):
            st.markdown(default_q)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Searching university documents..."):
                answer, sources = ask_university(default_q)

            st.markdown(answer)
            if sources:
                with st.expander("📚 Sources (with page numbers)"):
                    for line in sources.split("\n"):
                        st.markdown(line)

        # Save to SQL
        save_chat(username, default_q, answer, sources)

        full_response = f"{answer}\n\n📚 **Sources:**\n{sources.replace(chr(10), chr(10) + '  ')}"
        st.session_state.uni_messages.append({
            "role": "assistant",
            "content": full_response
        })
        st.rerun()

# ══════════════════════════════════════════
# TAB 2 — TEST PREP ENGINE
# ══════════════════════════════════════════
with tab2:
    with st.container(border=True):
        st.subheader("📝 Test Preparation Engine")

        col1, col2, col3 = st.columns(3)
        with col1:
            difficulty = st.selectbox("📊 Difficulty Level", ["Easy", "Medium", "Hard"])
        with col2:
            num_questions = st.slider("🔢 Number of Questions", 3, 10, 5)
        with col3:
            st.markdown("####  ")
            generate_btn = st.button("🚀 Generate MCQs", use_container_width=True, type="primary")

    if generate_btn:
        syllabus_path = st.session_state.get("syllabus_path")
        if not syllabus_path:
            pdfs = [f for f in os.listdir("data/pdfs") if f.endswith(".pdf")]
            if pdfs:
                syllabus_path = os.path.join("data/pdfs", pdfs[0])
            else:
                st.markdown(render_notice("Please upload a syllabus PDF first!", is_warning=True), unsafe_allow_html=True)
                st.stop()

        doc = fitz.open(syllabus_path)
        syllabus_text = "".join([page.get_text() for page in doc])

        with st.spinner("🤖 Running agent pipeline... (30-60 seconds)"):
            mcqs = generate_mcqs_with_agents(syllabus_text, difficulty, num_questions)

        if mcqs:
            st.session_state["mcqs"] = mcqs
            st.session_state["difficulty"] = difficulty
            st.session_state["answers"] = {}
            st.session_state["submitted"] = False
            st.rerun()
        else:
            st.error("❌ Failed to generate MCQs. Please try again.")

    if "mcqs" in st.session_state and st.session_state["mcqs"]:
        mcqs = st.session_state["mcqs"]
        difficulty = st.session_state.get("difficulty", "Medium")
        submitted = st.session_state.get("submitted", False)
        colors = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}

        st.markdown(f"## {colors[difficulty]} {difficulty} MCQs")
        st.markdown(f"*{len(mcqs)} questions — attempt all before submitting*")
        st.divider()

        answers = st.session_state.get("answers", {})

        for i, q in enumerate(mcqs):
            is_challenge = q.get("is_challenge", False)
            with st.container(border=True):
                difficulty_badge = f'<span class="mcq-badge badge-{difficulty.lower()}">{difficulty}</span>'
                if is_challenge:
                    difficulty_badge += ' <span class="mcq-badge badge-challenge">🔥 Challenge</span>'
                
                st.markdown(f"""
                {difficulty_badge}
                <div style="font-size: 1.1rem; font-weight: 600; color: #1f2937; margin-top: 4px; margin-bottom: 16px; line-height: 1.45;">
                    Q{i+1}. {q['question']}
                </div>
                """, unsafe_allow_html=True)

                options = q.get("options", {})
                option_list = [f"{k}) {v}" for k, v in options.items()]

                if not submitted:
                    selected = st.radio(
                        f"Select answer for Q{i+1}",
                        option_list,
                        key=f"q_{i}",
                        index=None,
                        label_visibility="collapsed"
                    )
                    answers[i] = selected[0] if selected else None
                else:
                    correct = q.get("answer", "")
                    user_ans = answers.get(i)
                    for opt in option_list:
                        letter = opt[0]
                        if letter == correct and letter == user_ans:
                            st.markdown(f'<div style="background-color: #ecfdf5; border: 1px solid #a7f3d0; padding: 10px 14px; border-radius: 8px; color: #047857; margin-bottom: 8px; font-weight: 500;">✅ {opt} <span style="font-size: 0.8rem; font-weight: normal; opacity: 0.8; margin-left: 8px;">(Your Answer - Correct!)</span></div>', unsafe_allow_html=True)
                        elif letter == correct:
                            st.markdown(f'<div style="background-color: #f0fdf4; border: 1px dashed #a7f3d0; padding: 10px 14px; border-radius: 8px; color: #047857; margin-bottom: 8px;">✅ {opt} <span style="font-size: 0.8rem; opacity: 0.8; margin-left: 8px;">(Correct Answer)</span></div>', unsafe_allow_html=True)
                        elif letter == user_ans:
                            st.markdown(f'<div style="background-color: #fef2f2; border: 1px solid #fecaca; padding: 10px 14px; border-radius: 8px; color: #b91c1c; margin-bottom: 8px; font-weight: 500;">❌ {opt} <span style="font-size: 0.8rem; font-weight: normal; opacity: 0.8; margin-left: 8px;">(Your Answer - Incorrect)</span></div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div style="color: #4b5563; padding: 10px 14px; margin-bottom: 8px; background-color: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb;">&nbsp;&nbsp;{opt}</div>', unsafe_allow_html=True)
                    
                    with st.expander("💡 See Explanation"):
                        st.markdown(q.get("explanation", ""))
                        st.caption(f"⏱️ Expected thinking time: {q.get('thinking_time', '')}")

        st.session_state["answers"] = answers

        col1, col2 = st.columns(2)
        if not submitted:
            with col1:
                if st.button("📤 Submit Answers", use_container_width=True, type="primary"):
                    st.session_state["submitted"] = True
                    st.rerun()
        else:
            score = sum(1 for i, q in enumerate(mcqs) if answers.get(i) == q.get("answer"))
            total = len(mcqs)
            percentage = round((score / total) * 100)

            if percentage >= 80:
                st.success(f"🏆 Score: {score}/{total} ({percentage}%) — Excellent!")
            elif percentage >= 50:
                st.warning(f"📊 Score: {score}/{total} ({percentage}%) — Good effort!")
            else:
                st.error(f"📉 Score: {score}/{total} ({percentage}%) — Keep practicing!")

            with col1:
                if st.button("🔄 Try Again", use_container_width=True):
                    st.session_state["submitted"] = False
                    st.session_state["answers"] = {}
                    st.rerun()
            with col2:
                mcq_text = "\n\n".join([
                    f"Q{i+1}. {q['question']}\nA) {q['options'].get('A','')}\nB) {q['options'].get('B','')}\nC) {q['options'].get('C','')}\nD) {q['options'].get('D','')}\nAnswer: {q['answer']}\nExplanation: {q['explanation']}"
                    for i, q in enumerate(mcqs)
                ])
                st.download_button(
                    "📥 Download MCQs",
                    data=mcq_text,
                    file_name=f"mcqs_{difficulty.lower()}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

# ══════════════════════════════════════════
# TAB 3 (ADMIN) — ALL STUDENT MARKS
# ══════════════════════════════════════════
if username == "admin":
    with tab3:
        with st.container(border=True):
            st.subheader("📊 Student Marks & Attendance Dashboard")
            st.caption("Admin-only view — individual student averages and class analytics")

            col_a, col_b = st.columns([1, 3])
            with col_a:
                if st.button("🔄 Reload Excel into Database", use_container_width=True):
                    with st.spinner("Loading students.xlsx..."):
                        msg = load_excel_to_db()
                    st.success(msg)

            st.divider()

            try:
                df_all = get_all_students()
            except Exception:
                df_all = None

            if df_all is None or df_all.empty:
                st.markdown(render_notice("No data found. Click 'Reload Excel into Database' above to load data/students.xlsx", is_warning=True), unsafe_allow_html=True)
                st.stop()

            # ─── Class Summary ───
            summary = get_class_summary()
            low_att_color = "#b91c1c" if summary["low_attendance_count"] > 0 else "#047857"
            st.markdown(f"""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px;">
                <div class="glass-card" style="border-left: 4px solid #1d4ed8;">
                    <div class="card-title">Total Students</div>
                    <div class="card-value" style="color: #1d4ed8;">{summary["total_students"]}</div>
                    <div class="card-desc">Active enrollments loaded</div>
                </div>
                <div class="glass-card" style="border-left: 4px solid #047857;">
                    <div class="card-title">Class Average</div>
                    <div class="card-value" style="color: #047857;">{summary["class_average"]}</div>
                    <div class="card-desc">Average score out of 100</div>
                </div>
                <div class="glass-card" style="border-left: 4px solid #6d28d9;">
                    <div class="card-title">Avg Attendance</div>
                    <div class="card-value" style="color: #6d28d9;">{summary["avg_attendance"]}%</div>
                    <div class="card-desc">Classwide attendance average</div>
                </div>
                <div class="glass-card" style="border-left: 4px solid {low_att_color};">
                    <div class="card-title">Low Attendance</div>
                    <div class="card-value" style="color: {low_att_color};">{summary["low_attendance_count"]}</div>
                    <div class="card-desc">Students below 75% threshold</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # ─── Individual Student Lookup ───
            st.markdown("### 🔍 Individual Student Lookup")
            roll_options = df_all["Roll No"].tolist()
            selected_roll = st.selectbox(
                "Select Roll Number",
                roll_options,
                format_func=lambda r: f"{r} — {df_all[df_all['Roll No']==r]['Name'].values[0]}"
            )

            if selected_roll:
                student = get_student_by_roll(int(selected_roll))
                if student:
                    status_color = "#047857" if student["status"] == "Good Standing" else "#b91c1c"
                    st.markdown(f"""
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-top: 12px; margin-bottom: 20px;">
                        <div class="glass-card" style="border-left: 4px solid #1d4ed8;">
                            <div class="card-title">Student Name</div>
                            <div class="card-value" style="font-size: 1.8rem; color: #1d4ed8;">{student["name"]}</div>
                            <div class="card-desc">Roll No: {student["roll_no"]}</div>
                        </div>
                        <div class="glass-card" style="border-left: 4px solid #047857;">
                            <div class="card-title">Average Marks</div>
                            <div class="card-value" style="color: #047857;">{student["average"]}</div>
                            <div class="card-desc">Total: {student["total"]} / 300</div>
                        </div>
                        <div class="glass-card" style="border-left: 4px solid {status_color};">
                            <div class="card-title">Attendance & Status</div>
                            <div class="card-value" style="color: {status_color};">{student["attendance"]}%</div>
                            <div class="card-desc">Status: {student["status"]}</div>
                        </div>
                    </div>
                    
                    <h4 style="color: #1f2937; font-size: 1.1rem; font-weight: 600; margin-bottom: 12px;">Subject Breakdown</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-bottom: 24px;">
                        <div style="background: #ffffff; border: 1px solid #e5e7eb; padding: 12px 16px; border-radius: 10px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                            <div style="font-size: 0.8rem; color: #6b7280; margin-bottom: 4px;">ANN</div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: #1f2937;">{student['ann']}</div>
                        </div>
                        <div style="background: #ffffff; border: 1px solid #e5e7eb; padding: 12px 16px; border-radius: 10px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                            <div style="font-size: 0.8rem; color: #6b7280; margin-bottom: 4px;">OOSE</div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: #1f2937;">{student['oose']}</div>
                        </div>
                        <div style="background: #ffffff; border: 1px solid #e5e7eb; padding: 12px 16px; border-radius: 10px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                            <div style="font-size: 0.8rem; color: #6b7280; margin-bottom: 4px;">Deep Learning</div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: #1f2937;">{student['deep_learning']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()

            # ─── Full Class Table ───
            st.markdown("### 📋 Full Class Marks Table")
            st.markdown(to_html_table(df_all, is_marks_table=True), unsafe_allow_html=True)

            st.divider()

            # ─── Top Students ───
            col_top, col_low = st.columns(2)
            with col_top:
                st.markdown("### 🏆 Top 3 Students")
                st.markdown(to_html_table(get_top_students(3)), unsafe_allow_html=True)

            with col_low:
                st.markdown("### ⚠️ Low Attendance (<75%)")
                low_att = get_low_attendance_students(75)
                if low_att.empty:
                    st.success("All students meet the 75% attendance requirement!")
                else:
                    st.markdown(to_html_table(low_att), unsafe_allow_html=True)

# ══════════════════════════════════════════
# TAB 3 (STUDENT) — MY MARKS ONLY
# ══════════════════════════════════════════
else:
    with tab3:
        with st.container(border=True):
            st.subheader("📊 My Marks & Attendance")
            st.caption(f"Viewing your own academic record, {name}")

            student = get_student_by_name(name)

            if not student:
                st.markdown(render_notice("No marks record found for your name yet. Please contact admin to ensure your data is loaded.", is_warning=True), unsafe_allow_html=True)
            else:
                summary = get_class_summary()
                rank_info = get_student_rank(student["roll_no"])
                status_color = "#047857" if student["status"] == "Good Standing" else "#b91c1c"
                avg_delta = round(student["average"] - summary["class_average"], 2)
                delta_color = "#047857" if avg_delta >= 0 else "#b91c1c"
                delta_sign = "+" if avg_delta >= 0 else ""

                st.markdown(f"""
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
                    <div class="glass-card" style="border-left: 4px solid #1d4ed8;">
                        <div class="card-title">Roll Number</div>
                        <div class="card-value" style="color: #1d4ed8;">{student["roll_no"]}</div>
                        <div class="card-desc">Registered Roll ID</div>
                    </div>
                    <div class="glass-card" style="border-left: 4px solid #047857;">
                        <div class="card-title">My Average Marks</div>
                        <div class="card-value" style="color: #047857;">{student["average"]}</div>
                        <div class="card-desc">Total: {student["total"]} / 300</div>
                    </div>
                    <div class="glass-card" style="border-left: 4px solid {status_color};">
                        <div class="card-title">My Attendance</div>
                        <div class="card-value" style="color: {status_color};">{student["attendance"]}%</div>
                        <div class="card-desc">Status: {student["status"]}</div>
                    </div>
                    <div class="glass-card" style="border-left: 4px solid #b45309;">
                        <div class="card-title">Class Rank</div>
                        <div class="card-value" style="color: #b45309;">{rank_info['rank'] if rank_info else 'N/A'} <span style="font-size: 1rem; color: #6b7280;">/ {rank_info['total_students'] if rank_info else 'N/A'}</span></div>
                        <div class="card-desc">Based on class average</div>
                    </div>
                </div>
                
                <div style="background: #ffffff; border: 1px solid #e5e7eb; padding: 16px 20px; border-radius: 12px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <div>
                        <span style="font-size: 0.9rem; color: #6b7280; display: block;">Class Average Reference</span>
                        <span style="font-size: 1.4rem; font-weight: 700; color: #1f2937;">{summary["class_average"]}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 0.9rem; color: #6b7280; display: block;">Deviation</span>
                        <span style="font-size: 1.4rem; font-weight: 700; color: {delta_color};">{delta_sign}{avg_delta}</span>
                    </div>
                </div>

                <h3 style="color: #1f2937; font-size: 1.3rem; font-weight: 600; margin-bottom: 16px;">📋 Subject-wise Marks</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px;">
                    <div style="background: #ffffff; border: 1px solid #e5e7eb; padding: 16px; border-radius: 12px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                        <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 8px;">Artificial Neural Networks (ANN)</div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: #1f2937;">{student['ann']}</div>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e5e7eb; padding: 16px; border-radius: 12px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                        <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 8px;">Object Oriented Software Eng (OOSE)</div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: #1f2937;">{student['oose']}</div>
                    </div>
                    <div style="background: #ffffff; border: 1px solid #e5e7eb; padding: 16px; border-radius: 12px; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                        <div style="font-size: 0.85rem; color: #6b7280; margin-bottom: 8px;">Deep Learning</div>
                        <div style="font-size: 1.8rem; font-weight: 700; color: #1f2937;">{student['deep_learning']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if student["status"] == "Good Standing":
                    st.markdown(render_notice(f"Status: {student['status']} — Keep it up!"), unsafe_allow_html=True)
                else:
                    st.markdown(render_notice(f"Status: {student['status']} — Attendance below 75%. As per GITAM regulations, you may not be eligible for sessional exams.", is_warning=True), unsafe_allow_html=True)