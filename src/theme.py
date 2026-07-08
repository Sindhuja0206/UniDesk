import streamlit as st

CSS_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Global Font Override */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
}

/* Background gradient styling */
.stApp {
    background: radial-gradient(circle at 50% 50%, #1E1B4B 0%, #0F172A 100%) !important;
}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #111827 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

/* Style main container padding */
.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Glassmorphism KPI Card Styles */
.glass-card {
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    margin-bottom: 20px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.glass-card:hover {
    border-color: rgba(124, 58, 237, 0.3);
    transform: translateY(-2px);
}
.card-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}
.card-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1;
    margin-bottom: 6px;
}
.card-desc {
    font-size: 0.8rem;
    color: #64748B;
}

/* Custom Button Styling */
.stButton > button {
    background: linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%) !important;
    color: #F8FAFC !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.4rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%) !important;
    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4) !important;
    transform: translateY(-2px) !important;
    color: #FFFFFF !important;
}
.stButton > button:active {
    transform: translateY(1px) !important;
}

/* Make secondary/secondary-like buttons look different if they are not primary */
.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #E2E8F0 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #FFFFFF !important;
}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(30, 41, 59, 0.6) !important;
    padding: 8px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
}
.stTabs [data-baseweb="tab"] {
    height: auto !important;
    padding: 10px 20px !important;
    background-color: transparent !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    color: #94A3B8 !important;
    border: none !important;
    transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #F8FAFC !important;
    background-color: rgba(255, 255, 255, 0.03) !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25) !important;
}
.stTabs [data-baseweb="tab-highlight-bar"] {
    display: none !important;
}

/* Style Bordered Containers as Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
    margin-bottom: 16px !important;
}

/* Form inputs styling */
.stTextInput input, .stSelectbox [role="combobox"], .stSlider, .stFileUploader {
    background-color: rgba(15, 23, 42, 0.6) !important;
    border-radius: 8px !important;
}
.stTextInput input {
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #F8FAFC !important;
}
.stTextInput input:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2) !important;
}

/* Badges for MCQs */
.mcq-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-right: 6px;
    margin-bottom: 8px;
}
.badge-easy { background: rgba(16, 185, 129, 0.12) !important; color: #34D399 !important; border: 1px solid rgba(16, 185, 129, 0.2) !important; }
.badge-medium { background: rgba(245, 158, 11, 0.12) !important; color: #FBBF24 !important; border: 1px solid rgba(245, 158, 11, 0.2) !important; }
.badge-hard { background: rgba(239, 68, 68, 0.12) !important; color: #FCA5A5 !important; border: 1px solid rgba(239, 68, 68, 0.2) !important; }
.badge-challenge { background: rgba(239, 68, 68, 0.2) !important; color: #FCA5A5 !important; border: 1px solid #EF4444 !important; }

/* Custom styled dataframe borders & headers */
.stDataFrame {
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Custom styled chat messages */
[data-testid="stChatMessage"] {
    background-color: rgba(30, 41, 59, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}
</style>
"""

def inject_theme():
    """Inject global CSS theme stylesheet."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

def get_header_banner(name: str) -> str:
    """Get the HTML string for the header banner."""
    return f"""
    <div style="background: linear-gradient(135deg, rgba(124, 58, 237, 0.15) 0%, rgba(79, 70, 229, 0.05) 100%); padding: 24px; border-radius: 16px; border: 1px solid rgba(124, 58, 237, 0.25); margin-bottom: 24px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);">
        <h1 style="margin: 0; color: #FFFFFF; font-size: 2.2rem; font-weight: 700; display: flex; align-items: center; gap: 12px;">
            🎓 University System Dashboard
        </h1>
        <p style="margin: 8px 0 0 0; color: #94A3B8; font-size: 0.95rem;">
            Welcome, <span style="color: #F8FAFC; font-weight: 600;">{name}</span> | Powered by LangGraph + LangChain + Groq
        </p>
    </div>
    """
