import streamlit as st
import os
import io
import json
import time
from services.rag_service import RAGService
from services.resume_service import ResumeService
from services.visualization_service import VisualizationService
from services.interview_tips_service import InterviewTipsService
from services.database_service import init_db, get_user_profile, save_resume_analysis
from services.jd_service import JDService
from services.practice_service import PracticeService
from services.mock_interview_service import MockInterviewService
from config import RESUME_UPLOAD_PATH

init_db()

st.set_page_config(
    page_title="AI求职面试助手 | InterviewAI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-primary: #0f0f1a;
    --bg-secondary: #1a1a2e;
    --bg-tertiary: #252540;
    --bg-card: rgba(26, 26, 46, 0.8);
    --accent-purple: #6c5ce7;
    --accent-cyan: #00cec9;
    --accent-gold: #fdcb6e;
    --accent-pink: #fd79a8;
    --text-primary: #ffffff;
    --text-secondary: #a2a8bd;
    --text-muted: #6b7280;
    --border: rgba(255, 255, 255, 0.08);
    --border-light: rgba(255, 255, 255, 0.12);
}

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

.stApp {
    background: var(--bg-primary) !important;
    background-image: 
        radial-gradient(at 20% 30%, rgba(108, 92, 231, 0.08) 0px, transparent 50%),
        radial-gradient(at 80% 20%, rgba(0, 206, 201, 0.05) 0px, transparent 50%),
        radial-gradient(at 40% 80%, rgba(253, 203, 110, 0.03) 0px, transparent 50%);
    min-height: 100vh;
}

.block-container {
    padding-top: 1rem !important;
    max-width: 1400px !important;
    padding-bottom: 2rem !important;
}

div[data-testid="stHeader"] {
    background: rgba(15, 15, 26, 0.9) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
}

div[data-testid="stSidebar"] {
    background: rgba(26, 26, 46, 0.95) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid var(--border);
    padding: 1.5rem 0 !important;
}

div[data-testid="stSidebarNav"] {
    padding-top: 0;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.65rem 1rem;
    margin: 0.1rem 0.5rem;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    color: var(--text-secondary);
    font-weight: 500;
    font-size: 0.9rem;
}

.nav-item:hover {
    background: rgba(108, 92, 231, 0.15);
    color: var(--text-primary);
    transform: translateX(2px);
}

.nav-item.active {
    background: linear-gradient(135deg, rgba(108, 92, 231, 0.3), rgba(0, 206, 201, 0.1));
    color: var(--accent-cyan);
    border-left: 3px solid var(--accent-purple);
}

.nav-item-icon {
    font-size: 1.1rem;
    width: 24px;
    text-align: center;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

h1 {
    font-size: 2.5rem !important;
    line-height: 1.15;
}

h2 {
    font-size: 1.75rem !important;
}

h3 {
    font-size: 1.25rem !important;
}

p, span, div {
    color: var(--text-secondary);
}

label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select,
.stNumberInput input {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus {
    border-color: var(--accent-purple) !important;
    box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.2) !important;
    outline: none !important;
}

.stTextInput label, .stTextArea label, .stSelectbox label, .stFileUploader label {
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    margin-bottom: 0.4rem !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent-purple) 0%, #5b4cdb 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 11px 24px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 15px rgba(108, 92, 231, 0.35) !important;
    letter-spacing: 0.01em !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(108, 92, 231, 0.5) !important;
    background: linear-gradient(135deg, #7c6ce8 0%, #6b5cec 100%) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

.stButton > button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
}

div[data-testid="stFileUploader"] {
    background: var(--bg-tertiary) !important;
    border: 2px dashed var(--border-light) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: var(--accent-purple) !important;
    background: rgba(108, 92, 231, 0.05) !important;
}

div[data-testid="stFileUploader"] p {
    color: var(--text-muted) !important;
}

div[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    margin-bottom: 0.75rem !important;
    overflow: hidden;
    transition: all 0.2s ease !important;
}

div[data-testid="stExpander"]:hover {
    border-color: var(--border-light) !important;
}

div[data-testid="stExpander"] summary {
    padding: 1rem 1.25rem !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    background: var(--bg-secondary);
}

div[data-testid="stExpander"] summary:hover {
    background: var(--bg-tertiary) !important;
}

div[data-testid="stExpander"] details[open] {
    background: var(--bg-card) !important;
}

.stSpinner > div {
    border-color: rgba(108, 92, 231, 0.2) !important;
    border-top-color: var(--accent-purple) !important;
}

div[data-testid="stImage"] {
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}

.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.card:hover {
    transform: translateY(-2px);
    border-color: var(--border-light);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

.card-glow {
    background: linear-gradient(135deg, rgba(108, 92, 231, 0.1), rgba(0, 206, 201, 0.05));
    border: 1px solid rgba(108, 92, 231, 0.2);
}

.card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.card-content {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.7;
}

.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1.5;
}

.badge-purple {
    background: rgba(108, 92, 231, 0.2);
    color: var(--accent-purple);
}

.badge-cyan {
    background: rgba(0, 206, 201, 0.2);
    color: var(--accent-cyan);
}

.badge-gold {
    background: rgba(253, 203, 110, 0.2);
    color: var(--accent-gold);
}

.badge-pink {
    background: rgba(253, 121, 168, 0.2);
    color: var(--accent-pink);
}

.badge-green {
    background: rgba(0, 255, 136, 0.2);
    color: #00ff88;
}

.badge-amber {
    background: rgba(251, 146, 60, 0.2);
    color: #fb923c;
}

.badge-rose {
    background: rgba(244, 63, 94, 0.2);
    color: #f43f5e;
}

.badge-gray {
    background: rgba(107, 114, 128, 0.2);
    color: var(--text-muted);
}

.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem;
    text-align: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan));
}

.stat-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 35px rgba(108, 92, 231, 0.2);
    border-color: rgba(108, 92, 231, 0.3);
}

.stat-number {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    color: var(--text-muted);
    font-size: 0.8rem;
    margin-top: 0.5rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.progress-bar {
    height: 8px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 0.5rem;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan));
    border-radius: 4px;
    transition: width 0.5s ease;
    position: relative;
}

.progress-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

div[data-testid="stAlertContainer"] {
    background: rgba(0, 255, 136, 0.1) !important;
    border: 1px solid rgba(0, 255, 136, 0.3) !important;
    border-radius: 12px !important;
    color: #00ff88 !important;
}

div[data-testid="stAlertContainer"] p {
    color: #00ff88 !important;
}

div[data-testid="stWarning"] {
    background: rgba(251, 146, 60, 0.1) !important;
    border: 1px solid rgba(251, 146, 60, 0.3) !important;
    border-radius: 12px !important;
    color: #fb923c !important;
}

div[data-testid="stWarning"] p {
    color: #fb923c !important;
}

div[data-testid="stError"] {
    background: rgba(244, 63, 94, 0.1) !important;
    border: 1px solid rgba(244, 63, 94, 0.3) !important;
    border-radius: 12px !important;
    color: #f43f5e !important;
}

div[data-testid="stError"] p {
    color: #f43f5e !important;
}

div[data-testid="stInfo"] {
    background: rgba(0, 206, 201, 0.1) !important;
    border: 1px solid rgba(0, 206, 201, 0.3) !important;
    border-radius: 12px !important;
    color: var(--accent-cyan) !important;
}

div[data-testid="stInfo"] p {
    color: var(--accent-cyan) !important;
}

::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--accent-purple);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: #7c6ce8;
}

.score-ring {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: conic-gradient(var(--accent-purple) var(--score, 75%), var(--bg-tertiary) 0);
    position: relative;
    transition: all 0.3s ease;
}

.score-ring::before {
    content: '';
    position: absolute;
    inset: 8px;
    background: var(--bg-secondary);
    border-radius: 50%;
}

.score-ring span {
    position: relative;
    z-index: 1;
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text-primary);
}

.score-ring.large {
    width: 150px;
    height: 150px;
}

.score-ring.large span {
    font-size: 2.25rem;
}

.interview-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.interview-card:hover {
    border-color: rgba(108, 92, 231, 0.3);
}

.question-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    margin-right: 0.75rem;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
}

.hero-section {
    padding: 3rem 0;
    text-align: left;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--text-primary), var(--accent-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 1rem;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: var(--text-secondary);
    line-height: 1.7;
    max-width: 600px;
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1.25rem;
    margin-top: 2rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.section-title::before {
    content: '';
    width: 4px;
    height: 1.5rem;
    background: linear-gradient(180deg, var(--accent-purple), var(--accent-cyan));
    border-radius: 2px;
}

.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 2rem;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.feature-card::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, rgba(108, 92, 231, 0.1) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 40px rgba(108, 92, 231, 0.2);
    border-color: rgba(108, 92, 231, 0.4);
}

.feature-card:hover::after {
    opacity: 1;
}

.feature-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 1.25rem;
    transition: transform 0.3s ease;
}

.feature-card:hover .feature-icon {
    transform: scale(1.1);
}

.feature-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.feature-desc {
    font-size: 0.875rem;
    color: var(--text-secondary);
    line-height: 1.6;
}

.glass-nav {
    background: rgba(26, 26, 46, 0.8);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 16px;
    padding: 0.5rem;
    margin-bottom: 1.5rem;
}

.glow-text {
    text-shadow: 0 0 30px rgba(108, 92, 231, 0.5);
}

.fade-in {
    animation: fadeIn 0.5s ease forwards;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.gradient-text {
    background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.tag-cloud-item {
    display: inline-block;
    padding: 0.4rem 1rem;
    background: rgba(108, 92, 231, 0.15);
    border-radius: 9999px;
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin: 0.3rem;
    transition: all 0.2s ease;
    cursor: default;
}

.tag-cloud-item:hover {
    background: rgba(108, 92, 231, 0.3);
    color: var(--accent-cyan);
    transform: translateY(-1px);
}

@media (max-width: 768px) {
    h1 { font-size: 1.75rem !important; }
    .hero-title { font-size: 2rem; }
    .stat-number { font-size: 1.5rem; }
    .feature-card { padding: 1.5rem; }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

@st.cache_resource
def get_services():
    return (
        RAGService(),
        ResumeService(),
        VisualizationService(),
        InterviewTipsService(),
        JDService(),
        PracticeService(),
        MockInterviewService()
    )

(rag_service, resume_service, visualization_service, 
 interview_tips_service, jd_service, practice_service, 
 mock_interview_service) = get_services()

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0 2rem 0; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem;">
            <div style="font-size: 2.25rem; font-weight: 800; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; letter-spacing: -0.03em;">
                InterviewAI
            </div>
            <p style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.5rem; letter-spacing: 0.2em; text-transform: uppercase;">
                AI Job Assistant
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        stats = practice_service.get_stats()
        
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem; padding: 1rem; background: var(--bg-tertiary); border-radius: 14px; border: 1px solid var(--border);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-secondary);">总体进度</span>
                <span style="font-size: 1rem; font-weight: 800; background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{stats['overall_progress']}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {stats['overall_progress']}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.75rem; background: rgba(108, 92, 231, 0.1); border-radius: 12px;">
                <div style="font-size: 1.5rem; font-weight: 800; color: var(--accent-purple);">{stats['mastered']}</div>
                <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.2rem;">已掌握</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.75rem; background: rgba(0, 206, 201, 0.1); border-radius: 12px;">
                <div style="font-size: 1.5rem; font-weight: 800; color: var(--accent-cyan);">{stats['practiced']}</div>
                <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.2rem;">已练习</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("<div style='font-size: 0.75rem; font-weight: 600; color: var(--text-muted); margin-bottom: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase;'>分类进度</div>", unsafe_allow_html=True)
        
        for cat_stat in stats['category_stats'][:5]:
            st.markdown(f"""
            <div style="margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span style="font-size: 0.8rem; color: var(--text-secondary);">{cat_stat['category']}</span>
                    <span style="font-size: 0.8rem; font-weight: 600; color: var(--accent-cyan);">{cat_stat['progress']}%</span>
                </div>
                <div class="progress-bar" style="height: 4px;">
                    <div class="progress-fill" style="width: {cat_stat['progress']}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def page_dashboard():
    stats = practice_service.get_stats()
    
    st.markdown("""
    <div class="hero-section">
        <div style="font-size: 0.9rem; font-weight: 600; color: var(--accent-purple); margin-bottom: 0.75rem; letter-spacing: 0.15em; text-transform: uppercase;">
            AI 智能求职助手
        </div>
        <h1 class="hero-title">
            准备好拿下你的<br>Dream Job 了吗？
        </h1>
        <p class="hero-subtitle">
            一站式AI求职助手，帮你简历优化、刷题练习、模拟面试，全面提升求职竞争力
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['total_questions']}</div>
            <div class="stat-label">题库总数</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['practiced']}</div>
            <div class="stat-label">已练习</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['mastered']}</div>
            <div class="stat-label">已掌握</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{len(practice_service.get_categories())}</div>
            <div class="stat-label">技术分类</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("<div class='section-title'>功能模块</div>", unsafe_allow_html=True)
        
        feat_col1, feat_col2 = st.columns(2)
        
        with feat_col1:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon" style="background: linear-gradient(135deg, rgba(108, 92, 231, 0.3), rgba(108, 92, 231, 0.1)); color: var(--accent-purple);">📝</div>
                <div class="feature-title">刷题练习</div>
                <div class="feature-desc">精选面试题库，支持分类练习、收藏、错题复习，基于艾宾浩斯遗忘曲线智能安排复习计划</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon" style="background: linear-gradient(135deg, rgba(0, 206, 201, 0.3), rgba(0, 206, 201, 0.1)); color: var(--accent-cyan);">📄</div>
                <div class="feature-title">简历优化</div>
                <div class="feature-desc">AI智能分析简历，提取技能关键词，提供针对性优化建议，让你的简历脱颖而出</div>
            </div>
            """, unsafe_allow_html=True)
        
        with feat_col2:
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon" style="background: linear-gradient(135deg, rgba(253, 203, 110, 0.3), rgba(253, 203, 110, 0.1)); color: var(--accent-gold);">🎯</div>
                <div class="feature-title">模拟面试</div>
                <div class="feature-desc">多轮模拟面试，实时评分反馈，找出薄弱环节重点突破，提前体验真实面试流程</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="feature-card">
                <div class="feature-icon" style="background: linear-gradient(135deg, rgba(253, 121, 168, 0.3), rgba(253, 121, 168, 0.1)); color: var(--accent-pink);">📊</div>
                <div class="feature-title">JD匹配</div>
                <div class="feature-desc">上传岗位JD，AI分析技能差距，生成个性化学习计划，精准定位提升方向</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("<div class='section-title'>学习进度</div>", unsafe_allow_html=True)
        
        for cat_stat in stats['category_stats'][:6]:
            st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.35rem;">
                    <span style="font-size: 0.85rem; font-weight: 500; color: var(--text-primary);">{cat_stat['category']}</span>
                    <span style="font-size: 0.85rem; font-weight: 700; color: var(--accent-cyan);">{cat_stat['progress']}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {cat_stat['progress']}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def page_resume():
    st.markdown("""
    <div class="hero-section" style="padding: 1.5rem 0;">
        <h1 style="font-size: 2rem; margin: 0;">📄 简历智能优化</h1>
        <p style="color: var(--text-secondary); margin-top: 0.5rem;">让AI帮你打造完美简历</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="card card-glow">
            <div class="card-title">
                <span style="font-size: 1.25rem;">🤖</span>
                <span>AI简历深度分析</span>
                <span class="badge badge-purple">智能评估</span>
            </div>
            <div class="card-content">
                上传你的简历，AI将从多个维度进行深度分析，识别技能亮点和待改进点，
                并提供专业的优化建议，让你的简历在众多应聘者中脱颖而出。
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title"><span style="font-size: 1.25rem;">⚡</span><span>分析维度</span></div>
            <div class="card-content" style="font-size: 0.85rem;">
                ✓ 基本信息完整性<br>
                ✓ 技能关键词提取<br>
                ✓ 工作经历亮点识别<br>
                ✓ 项目经验评估<br>
                ✓ 针对性优化建议
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("选择简历文件（PDF格式）", type="pdf", key="resume_upload")
    target_position = st.text_input("目标岗位（选填，提供更精准建议）", "", key="resume_target_pos", placeholder="例如：Python后端工程师")
    
    if uploaded_file is not None:
        file_path = os.path.join(RESUME_UPLOAD_PATH, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success("✅ 简历上传成功！")
        
        with st.spinner("正在解析简历..."):
            resume_text = resume_service.extract_text_from_pdf(file_path)
        
        with st.expander("📝 查看简历原文", expanded=False):
            st.text_area("", resume_text, height=200, key="resume_text_view")
        
        btn1, btn2 = st.columns(2)
        with btn1:
            analyze_clicked = st.button("🔍 分析简历", use_container_width=True)
        with btn2:
            optimize_clicked = st.button("✨ 优化建议", use_container_width=True)
        
        if analyze_clicked:
            with st.spinner("AI正在深度分析你的简历..."):
                analysis = resume_service.analyze_resume(resume_text, target_position)
            
            st.markdown("### 📊 分析报告")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("""
                <div class="card">
                    <div class="card-title"><span>👤</span><span>基本信息</span></div>
                </div>
                """, unsafe_allow_html=True)
                st.write(analysis.get("basic_info", "暂无"))
                
                st.markdown("""
                <div class="card">
                    <div class="card-title"><span>🛠</span><span>技能清单</span></div>
                </div>
                """, unsafe_allow_html=True)
                skills = analysis.get("skills", [])
                if skills:
                    for s in skills:
                        name = s.get('skill_name', '')
                        prof = s.get('proficiency', '')
                        st.markdown(f"<span class='tag-cloud-item'>{name} · {prof}</span>", unsafe_allow_html=True)
            with c2:
                st.markdown("""
                <div class="card">
                    <div class="card-title"><span>✨</span><span>亮点</span></div>
                </div>
                """, unsafe_allow_html=True)
                for i, h in enumerate(analysis.get("experience_highlights", [])[:5], 1):
                    st.markdown(f"<div style='padding: 0.5rem 0; color: var(--accent-cyan);'>{i}. {h}</div>", unsafe_allow_html=True)
                
                st.markdown("""
                <div class="card">
                    <div class="card-title"><span>📈</span><span>待改进</span></div>
                </div>
                """, unsafe_allow_html=True)
                for i, g in enumerate(analysis.get("experience_gaps", [])[:5], 1):
                    st.markdown(f"<div style='padding: 0.5rem 0; color: var(--accent-gold);'>{i}. {g}</div>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class="card card-glow">
                <div class="card-title"><span>💡</span><span>优化建议</span></div>
            </div>
            """, unsafe_allow_html=True)
            for i, s in enumerate(analysis.get("suggestions", [])[:8], 1):
                st.markdown(f"<div style='padding: 0.4rem 0; color: var(--text-secondary);'>{i}. {s}</div>", unsafe_allow_html=True)
            
            save_resume_analysis({
                "file_name": uploaded_file.name,
                "resume_text": resume_text,
                "target_position": target_position,
                "analysis": analysis,
                "suggestions": "",
                "skills": analysis.get("skills", [])
            })
        
        if optimize_clicked:
            with st.spinner("AI正在生成个性化优化方案..."):
                suggestions = resume_service.optimize_resume(resume_text, target_position)
            
            st.markdown("### ✨ 优化建议")
            st.markdown(f"""
            <div class="card card-glow">
                <div class="card-content">{suggestions}</div>
            </div>
            """, unsafe_allow_html=True)

def page_practice():
    st.markdown("""
    <div class="hero-section" style="padding: 1.5rem 0;">
        <h1 style="font-size: 2rem; margin: 0;">📝 刷题练习</h1>
        <p style="color: var(--text-secondary); margin-top: 0.5rem;">智能刷题，高效备考</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="card card-glow">
            <div class="card-title">
                <span style="font-size: 1.25rem;">🎯</span>
                <span>智能刷题系统</span>
                <span class="badge badge-cyan">艾宾浩斯复习</span>
            </div>
            <div class="card-content">
                精选面试题库，支持分类练习、收藏、错题复习，基于艾宾浩斯遗忘曲线智能安排复习计划，让每一次练习都更有价值
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        stats = practice_service.get_stats()
        st.markdown(f"""
        <div class="stat-card" style="padding: 1.5rem;">
            <div class="stat-number">{stats['overall_progress']}%</div>
            <div class="stat-label">总进度</div>
            <div class="progress-bar" style="margin-top: 0.75rem;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    mode = st.radio("选择模式", ["📚 分类浏览", "🎲 随机练习", "⭐ 我的收藏", "🔄 待复习"], horizontal=True)
    
    if mode == "📚 分类浏览":
        categories = practice_service.get_categories()
        selected_cat = st.selectbox("选择分类", categories)
        
        questions = practice_service.get_questions_by_category(selected_cat)
        st.info(f"共 {len(questions)} 道{selected_cat}面试题")
        
        for i, q in enumerate(questions, 1):
            diff_text = {1: "简单", 2: "中等", 3: "困难"}.get(q.get('difficulty', 2), "中等")
            diff_badge = {1: "badge-green", 2: "badge-amber", 3: "badge-rose"}.get(q.get('difficulty', 2), "badge-amber")
            
            with st.expander(f"{i}. {q['question']}"):
                st.markdown(f"""
                <div style="display: flex; gap: 0.75rem; margin-bottom: 1rem;">
                    <span class="badge badge-purple">{q.get('sub_category', '')}</span>
                    <span class="badge {diff_badge}">{diff_text}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 参考答案")
                st.write(q['answer'])
                
                if q.get('key_points'):
                    st.markdown("#### 🎯 考察要点")
                    for kp in q['key_points']:
                        st.markdown(f"- <span style='color: var(--accent-cyan);'>{kp}</span>", unsafe_allow_html=True)
                
                if q.get('follow_ups'):
                    st.markdown("#### ❓ 常见追问")
                    for fu in q['follow_ups'][:3]:
                        st.markdown(f"- <span style='color: var(--text-secondary);'>{fu}</span>", unsafe_allow_html=True)
    
    elif mode == "🎲 随机练习":
        if 'practice_questions' not in st.session_state:
            st.session_state.practice_questions = []
            st.session_state.practice_idx = 0
            st.session_state.practice_score = 0
        
        col_a, col_b = st.columns([1, 3])
        with col_a:
            cat_options = ["全部"] + practice_service.get_categories()
            selected = st.selectbox("选择题库", cat_options, key="practice_cat")
            count = st.slider("题目数量", 3, 15, 5)
        with col_b:
            st.write("")
            st.write("")
            if st.button("🎲 开始练习", use_container_width=True):
                cat = None if selected == "全部" else selected
                st.session_state.practice_questions = practice_service.get_random_questions(cat, count)
                st.session_state.practice_idx = 0
                st.session_state.practice_score = 0
        
        if st.session_state.practice_questions:
            q_list = st.session_state.practice_questions
            idx = st.session_state.practice_idx
            
            if idx < len(q_list):
                q = q_list[idx]
                
                st.markdown(f"""
                <div class="interview-card">
                    <div style="display: flex; align-items: center; margin-bottom: 1.25rem;">
                        <span class="question-number">{idx + 1}</span>
                        <div>
                            <span class="badge badge-purple" style="margin-right: 0.5rem;">{q.get('category', '')}</span>
                            <span class="badge badge-gray">{ {1:'简单',2:'中等',3:'困难'}.get(q.get('difficulty',2), '中等') }</span>
                        </div>
                        <span style="margin-left: auto; color: var(--text-muted); font-size: 0.85rem;">{idx + 1}/{len(q_list)}</span>
                    </div>
                    <h3 style="margin: 0; font-size: 1.25rem; line-height: 1.6; color: var(--text-primary);">{q['question']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                user_ans = st.text_area("你的回答", height=150, key=f"practice_ans_{idx}", placeholder="写下你的答案...")
                
                btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
                with btn_col1:
                    if st.button("✅ 提交答案", use_container_width=True):
                        if user_ans:
                            result = practice_service.check_answer(q, user_ans)
                            st.session_state.practice_score += result.get('score', 0)
                            
                            from services.database_service import save_question_record, get_question_record
                            import datetime
                            
                            old_rec = get_question_record(q['id'])
                            review_count = old_rec['review_count'] + 1 if old_rec else 1
                            
                            next_review = practice_service.calculate_next_review(result.get('score', 60), review_count)
                            
                            save_question_record({
                                'question_id': q['id'],
                                'category': q.get('category'),
                                'is_correct': 1 if result.get('score', 60) >= 70 else 0,
                                'answer_text': user_ans,
                                'is_collected': old_rec['is_collected'] if old_rec else 0,
                                'review_count': review_count,
                                'next_review_at': next_review,
                                'last_review_at': datetime.datetime.now().isoformat()
                            })
                            
                            st.success(f"评分：{result.get('score', 60)}分")
                            if result.get('strengths'):
                                st.markdown("**✅ 优点**")
                                for s in result['strengths']:
                                    st.markdown(f"- <span style='color: #00ff88;'>{s}</span>", unsafe_allow_html=True)
                            if result.get('weaknesses'):
                                st.markdown("**⚠️ 不足**")
                                for w in result['weaknesses']:
                                    st.markdown(f"- <span style='color: #fb923c;'>{w}</span>", unsafe_allow_html=True)
                        else:
                            st.warning("请先输入你的答案")
                
                with btn_col2:
                    if st.button("📖 看答案", use_container_width=True):
                        st.info(q['answer'])
                
                with btn_col3:
                    if st.button("➡️ 下一题", use_container_width=True):
                        st.session_state.practice_idx += 1
                        st.rerun()
            else:
                avg_score = st.session_state.practice_score / len(q_list) if q_list else 0
                st.balloons()
                st.markdown(f"""
                <div class="card" style="text-align: center; padding: 4rem;">
                    <h2 style="font-size: 2rem; color: var(--text-primary); margin-bottom: 2rem;">🎉 练习完成！</h2>
                    <div class="score-ring large" style="--score: {avg_score}%; margin: 0 auto 1.5rem auto;">
                        <span>{int(avg_score)}</span>
                    </div>
                    <p style="color: var(--text-muted); font-size: 1rem;">平均得分</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🔄 再来一组"):
                    st.session_state.practice_questions = []
                    st.session_state.practice_idx = 0
                    st.rerun()
    
    elif mode == "⭐ 我的收藏":
        from services.database_service import get_collected_questions
        collected = get_collected_questions()
        
        if not collected:
            st.info("还没有收藏的题目，去刷题模式收藏你认为重要的题目吧！")
        else:
            st.success(f"共收藏了 {len(collected)} 道题")
            for i, rec in enumerate(collected, 1):
                with st.expander(f"{i}. 题目 {rec['question_id']}"):
                    st.write(f"分类：{rec.get('category', '未知')}")
                    st.write(f"复习次数：{rec.get('review_count', 0)}")
                    if rec.get('answer_text'):
                        st.markdown("**你的回答**")
                        st.write(rec['answer_text'])
    
    elif mode == "🔄 待复习":
        from services.database_service import get_review_questions
        review_list = get_review_questions()
        
        if not review_list:
            st.success("🎉 太棒了！没有待复习的题目")
        else:
            st.info(f"有 {len(review_list)} 道题需要复习")
            for i, rec in enumerate(review_list, 1):
                with st.expander(f"{i}. 题目 {rec['question_id']}"):
                    st.write(f"分类：{rec.get('category', '未知')}")
                    st.write(f"已复习 {rec.get('review_count', 0)} 次")
                    st.write(f"上次复习：{rec.get('last_review_at', '未知')}")

def page_interview():
    st.markdown("""
    <div class="hero-section" style="padding: 1.5rem 0;">
        <h1 style="font-size: 2rem; margin: 0;">🎯 模拟面试</h1>
        <p style="color: var(--text-secondary); margin-top: 0.5rem;">体验真实面试流程</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="card card-glow">
            <div class="card-title">
                <span style="font-size: 1.25rem;">🤖</span>
                <span>AI模拟面试官</span>
                <span class="badge badge-pink">多轮对话</span>
            </div>
            <div class="card-content">
                体验真实面试流程，AI面试官会根据你的回答实时追问和评分，
                面试结束后生成详细的评估报告和改进建议，帮你提前适应真实面试场景
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title"><span style="font-size: 1.25rem;">📋</span><span>面试流程</span></div>
            <div class="card-content" style="font-size: 0.85rem;">
                1. 选择目标岗位<br>
                2. AI出题答题（5-10题）<br>
                3. 实时点评反馈<br>
                4. 生成综合评估报告
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = 'ready'
        st.session_state.interview_questions = []
        st.session_state.interview_idx = 0
        st.session_state.interview_answers = []
        st.session_state.interview_total_score = 0
    
    if st.session_state.interview_state == 'ready':
        pos_col1, pos_col2 = st.columns([1, 1])
        with pos_col1:
            position = st.text_input("目标岗位", "", key="interview_pos", placeholder="例如：Python后端工程师")
        with pos_col2:
            q_count = st.slider("题目数量", 3, 10, 5)
        
        if st.button("🚀 开始面试", use_container_width=True):
            with st.spinner("AI面试官正在准备题目..."):
                questions = mock_interview_service.start_interview(position, q_count)
                st.session_state.interview_questions = questions
                st.session_state.interview_idx = 0
                st.session_state.interview_answers = []
                st.session_state.interview_total_score = 0
                st.session_state.interview_state = 'ongoing'
                st.rerun()
    
    elif st.session_state.interview_state == 'ongoing':
        questions = st.session_state.interview_questions
        idx = st.session_state.interview_idx
        
        progress_pct = (idx / len(questions)) * 100
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: var(--text-muted); font-size: 0.9rem;">面试进度</span>
                <span style="color: var(--accent-purple); font-weight: 600;">{idx}/{len(questions)}</span>
            </div>
            <div class="progress-bar" style="height: 10px;">
                <div class="progress-fill" style="width: {progress_pct}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if idx < len(questions):
            q = questions[idx]
            q_type = q.get('type', '技术')
            type_badge = "badge-purple" if q_type == "技术" else "badge-amber"
            
            st.markdown(f"""
            <div class="interview-card">
                <div style="display: flex; align-items: center; margin-bottom: 1.25rem;">
                    <span class="question-number">{idx + 1}</span>
                    <div>
                        <span class="badge {type_badge}" style="margin-right: 0.5rem;">{q_type}</span>
                        <span class="badge badge-gray">{q.get('category', '')}</span>
                    </div>
                </div>
                <h3 style="margin: 0; font-size: 1.35rem; line-height: 1.7; color: var(--text-primary);">{q['question']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            user_answer = st.text_area("💬 你的回答", height=200, key=f"interview_ans_{idx}", 
                                        placeholder="请在这里输入你的回答，完成后点击提交...")
            
            btn_col1, btn_col2 = st.columns([1, 3])
            
            with btn_col1:
                submitted = st.button("✅ 提交回答", use_container_width=True)
            
            with btn_col2:
                show_hint = st.button("💡 提示一下", use_container_width=True)
            
            if show_hint:
                with st.expander("💡 答题思路提示", expanded=True):
                    answer = q.get('answer', '')
                    first_100 = answer[:150] + "..." if len(answer) > 150 else answer
                    st.info(first_100)
            
            if submitted:
                if not user_answer:
                    st.warning("请先输入你的回答")
                else:
                    with st.spinner("AI面试官正在点评..."):
                        result = mock_interview_service.evaluate_answer(
                            q, user_answer, idx + 1
                        )
                    
                    score = result.get('total_score', 60)
                    st.session_state.interview_total_score += score
                    st.session_state.interview_answers.append({
                        "question": q['question'],
                        "user_answer": user_answer,
                        "score": score,
                        "feedback": result.get('feedback', ''),
                        "type": q_type
                    })
                    
                    col_s1, col_s2 = st.columns([1, 3])
                    with col_s1:
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <div class="score-ring" style="--score: {score}%; margin: 0 auto;">
                                <span>{score}</span>
                            </div>
                            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.5rem;">本题得分</p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_s2:
                        st.markdown("### 📝 面试官点评")
                        st.write(result.get('feedback', ''))
                        
                        if result.get('strengths'):
                            st.markdown("**✅ 做得好的地方**")
                            for s in result['strengths']:
                                st.markdown(f"- <span style='color: #00ff88;'>{s}</span>", unsafe_allow_html=True)
                        
                        if result.get('improvements'):
                            st.markdown("**📈 可以改进**")
                            for imp in result['improvements']:
                                st.markdown(f"- <span style='color: #fb923c;'>{imp}</span>", unsafe_allow_html=True)
                    
                    if st.button("➡️ 下一题", use_container_width=True):
                        st.session_state.interview_idx += 1
                        st.rerun()
        else:
            st.session_state.interview_state = 'finished'
            st.rerun()
    
    elif st.session_state.interview_state == 'finished':
        questions = st.session_state.interview_questions
        answers = st.session_state.interview_answers
        total_score = st.session_state.interview_total_score
        avg_score = total_score / len(questions) if questions else 0
        
        with st.spinner("正在生成面试评估报告..."):
            summary = mock_interview_service.generate_summary(
                st.session_state.get('interview_pos', ''),
                answers, total_score, len(questions)
            )
        
        st.balloons()
        
        st.markdown("### 📊 面试评估报告")
        
        col_report_1, col_report_2 = st.columns([1, 2])
        with col_report_1:
            level_colors = {
                "优秀": "#00ff88", "良好": "#6c5ce7", 
                "合格": "#fdcb6e", "需努力": "#f43f5e"
            }
            level = summary.get('level', '良好')
            color = level_colors.get(level, "#6c5ce7")
            
            st.markdown(f"""
            <div class="card" style="text-align: center; padding: 2rem;">
                <div class="score-ring large" style="--score: {summary.get('overall_score', avg_score)}%; margin: 1rem auto 1.5rem auto;">
                    <span>{int(summary.get('overall_score', avg_score))}</span>
                </div>
                <div style="font-size: 1.75rem; font-weight: 800; color: {color}; margin-bottom: 0.5rem;">
                    {level}
                </div>
                <div style="color: var(--text-muted); font-size: 0.9rem;">综合评级</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number" style="font-size: 1.75rem;">{len(questions)}</div>
                <div class="stat-label">题目数量</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_report_2:
            st.markdown("""
            <div class="card card-glow">
                <div class="card-title"><span>📝</span><span>总体评价</span></div>
                <div class="card-content">""" + summary.get('overall_comment', '') + """</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="card">
                <div class="card-title"><span>💪</span><span>优势分析</span></div>
            </div>
            """, unsafe_allow_html=True)
            for s in summary.get('strengths', []):
                st.markdown(f"- ✅ <span style='color: #00ff88;'>{s}</span>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class="card">
                <div class="card-title"><span>📈</span><span>待提升点</span></div>
            </div>
            """, unsafe_allow_html=True)
            for w in summary.get('weaknesses', []):
                st.markdown(f"- ⚠️ <span style='color: #fb923c;'>{w}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📚 学习建议")
        for i, sug in enumerate(summary.get('study_suggestions', []), 1):
            st.markdown(f"""
            <div class="card" style="margin-bottom: 0.75rem; padding: 1rem 1.25rem; background: rgba(108, 92, 231, 0.05);">
                <div style="display: flex; gap: 1rem;">
                    <span style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan)); color: white; display: inline-flex; align-items: center; justify-content: center; font-size: 0.9rem; font-weight: 700; flex-shrink: 0;">{i}</span>
                    <div style="flex: 1; color: var(--text-secondary);">{sug}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔍 逐题回顾")
        
        for i, ans in enumerate(answers, 1):
            with st.expander(f"第{i}题 - {ans.get('type', '')} - {ans.get('score', 0)}分"):
                st.markdown(f"**问题：** <span style='color: var(--text-primary);'>{ans['question']}</span>", unsafe_allow_html=True)
                st.markdown(f"**你的回答：** <span style='color: var(--text-secondary);'>{ans['user_answer']}</span>", unsafe_allow_html=True)
                st.markdown(f"**点评：** <span style='color: var(--text-secondary);'>{ans.get('feedback', '')}</span>", unsafe_allow_html=True)
        
        if st.button("🔄 再来一次", use_container_width=True):
            st.session_state.interview_state = 'ready'
            st.session_state.interview_questions = []
            st.session_state.interview_idx = 0
            st.session_state.interview_answers = []
            st.session_state.interview_total_score = 0
            st.rerun()

def page_jd_match():
    st.markdown("""
    <div class="hero-section" style="padding: 1.5rem 0;">
        <h1 style="font-size: 2rem; margin: 0;">🎯 JD匹配分析</h1>
        <p style="color: var(--text-secondary); margin-top: 0.5rem;">精准定位技能差距</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="card card-glow">
            <div class="card-title">
                <span style="font-size: 1.25rem;">📋</span>
                <span>岗位JD智能分析</span>
                <span class="badge badge-amber">差距分析</span>
            </div>
            <div class="card-content">
                粘贴岗位招聘描述，AI自动提取技能要求，分析你与目标岗位的差距，
                并生成个性化的学习计划，助你精准提升
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title"><span style="font-size: 1.25rem;">✨</span><span>核心功能</span></div>
            <div class="card-content" style="font-size: 0.85rem;">
                ✓ 技能要求提取<br>
                ✓ 匹配度评分<br>
                ✓ 差距分析<br>
                ✓ 学习计划生成
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    jd_text = st.text_area("粘贴岗位JD", height=250, 
                            placeholder="在这里粘贴岗位招聘描述、任职要求等内容...",
                            key="jd_text_input")
    
    user_skills_text = st.text_input("你的主要技能（用逗号分隔，选填）", "", 
                                       key="user_skills_input",
                                       placeholder="例如：Python, Django, MySQL, Redis, Docker")
    
    btn_col1, btn_col2 = st.columns([1, 3])
    with btn_col1:
        analyze_btn = st.button("🔍 分析匹配度", use_container_width=True)
    
    if analyze_btn and jd_text:
        with st.spinner("AI正在分析岗位JD..."):
            user_skills = [s.strip() for s in user_skills_text.split(',') if s.strip()] if user_skills_text else []
            jd_info = jd_service.extract_jd_info(jd_text)
            match_result = jd_service.analyze_match(jd_text, user_skills)
            
            from services.database_service import save_jd_analysis
            save_jd_analysis({
                "company": jd_info.get('company'),
                "position": jd_info.get('position'),
                "location": jd_info.get('location'),
                "raw_text": jd_text,
                "extracted_skills": jd_info.get('skills', []),
                "match_score": match_result.get('match_score', 0),
                "gap_analysis": match_result,
                "ai_analysis": ''
            })
        
        match_score = match_result.get('match_score', 0)
        
        st.markdown("---")
        st.markdown("### 📊 匹配度分析")
        
        score_col, info_col = st.columns([1, 2])
        with score_col:
            score_color = "#00ff88" if match_score >= 80 else "#6c5ce7" if match_score >= 60 else "#fdcb6e" if match_score >= 40 else "#f43f5e"
            st.markdown(f"""
            <div class="card" style="text-align: center; padding: 2rem;">
                <div class="score-ring large" style="--score: {match_score}%; margin: 1rem auto 1.5rem auto;">
                    <span>{match_score}</span>
                </div>
                <div style="font-size: 1.5rem; font-weight: 800; color: {score_color};">
                    {"高度匹配" if match_score >= 80 else "基本匹配" if match_score >= 60 else "有差距" if match_score >= 40 else "差距较大"}
                </div>
                <div style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.25rem;">匹配度评分</div>
            </div>
            """, unsafe_allow_html=True)
            
            if jd_info.get('position'):
                st.markdown(f"""
                <div class="stat-card">
                    <div style="font-weight: 600; color: var(--text-primary); font-size: 1.1rem;">{jd_info.get('position', '')}</div>
                    <div style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.25rem;">{jd_info.get('company', '') or '未知公司'} · {jd_info.get('location', '') or '未知地点'}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with info_col:
            st.markdown("""
            <div class="card">
                <div class="card-title"><span>✅</span><span>已匹配技能</span></div>
            </div>
            """, unsafe_allow_html=True)
            matched = match_result.get('matched_skills', [])
            if matched:
                for s in matched[:8]:
                    st.markdown(f"<span class='tag-cloud-item'>{s}</span>", unsafe_allow_html=True)
            else:
                st.info("输入你的技能后可查看匹配情况")
            
            st.markdown("""
            <div class="card">
                <div class="card-title"><span>⚠️</span><span>待提升技能</span></div>
            </div>
            """, unsafe_allow_html=True)
            missing = match_result.get('missing_skills', [])
            if missing:
                for m in missing:
                    skill = m.get('skill_name', '')
                    priority = m.get('priority', 'medium')
                    p_badge = "badge-rose" if priority == "high" else "badge-amber" if priority == "medium" else "badge-gray"
                    p_text = "高优先级" if priority == "high" else "中优先级" if priority == "medium" else "低优先级"
                    st.markdown(f"<span class='tag-cloud-item'>{skill} · {p_text}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💡 差距分析与建议")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="card">
                <div class="card-title"><span>💪</span><span>你的优势</span></div>
            </div>
            """, unsafe_allow_html=True)
            for s in match_result.get('strengths', [])[:5]:
                st.markdown(f"- ✅ <span style='color: #00ff88;'>{s}</span>", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="card">
                <div class="card-title"><span>📈</span><span>待改进</span></div>
            </div>
            """, unsafe_allow_html=True)
            for w in match_result.get('weaknesses', [])[:5]:
                st.markdown(f"- ⚠️ <span style='color: #fb923c;'>{w}</span>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card card-glow">
            <div class="card-title"><span>📝</span><span>改进建议</span></div>
        </div>
        """, unsafe_allow_html=True)
        for i, sug in enumerate(match_result.get('suggestions', [])[:8], 1):
            st.markdown(f"<div style='padding: 0.4rem 0; color: var(--text-secondary);'>{i}. {sug}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("📚 生成学习计划", use_container_width=True):
            with st.spinner("AI正在为你定制学习计划..."):
                study_plan = jd_service.generate_study_plan(match_result, jd_info.get('position', ''))
                
                from services.database_service import save_study_plan
                save_study_plan({
                    "jd_id": None,
                    "title": f"{jd_info.get('position', '目标岗位')}学习计划",
                    "plan": study_plan,
                    "priority": 1,
                    "status": "in_progress",
                    "estimated_hours": sum(w.get('estimated_hours', 5) for w in study_plan)
                })
            
            st.markdown("### 📅 个性化学习计划")
            
            for week in study_plan:
                week_num = week.get('week', 1)
                theme = week.get('theme', '')
                hours = week.get('estimated_hours', 0)
                
                with st.expander(f"第{week_num}周 - {theme} ({hours}小时)", expanded=(week_num == 1)):
                    col_w1, col_w2 = st.columns(2)
                    with col_w1:
                        st.markdown("**📚 学习内容**")
                        for t in week.get('topics', []):
                            st.markdown(f"- <span style='color: var(--accent-cyan);'>{t}</span>", unsafe_allow_html=True)
                    with col_w2:
                        st.markdown("**🔗 推荐资源**")
                        for r in week.get('resources', []):
                            st.markdown(f"- <span style='color: var(--text-secondary);'>{r}</span>", unsafe_allow_html=True)
                    
                    st.markdown("**💻 实践练习**")
                    st.markdown(f"- <span style='color: var(--text-secondary);'>{week.get('practice', '')}</span>", unsafe_allow_html=True)
                    
                    st.markdown("**🎯 验收标准**")
                    st.markdown(f"- <span style='color: var(--text-secondary);'>{week.get('milestone', '')}</span>", unsafe_allow_html=True)

def page_rag():
    st.markdown("""
    <div class="hero-section" style="padding: 1.5rem 0;">
        <h1 style="font-size: 2rem; margin: 0;">🔍 智能问答</h1>
        <p style="color: var(--text-secondary); margin-top: 0.5rem;">基于知识库的精准问答</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="card card-glow">
            <div class="card-title">
                <span style="font-size: 1.25rem;">🧠</span>
                <span>RAG知识库问答</span>
                <span class="badge badge-cyan">语义检索</span>
            </div>
            <div class="card-content">
                基于面试题库的智能问答系统，输入你的问题，AI结合知识库为你提供精准答案，助你快速掌握面试要点
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title"><span style="font-size: 1.25rem;">📚</span><span>知识库</span></div>
            <div class="card-content" style="font-size: 0.85rem;">
                <span class="badge badge-purple">Python</span>
                <span class="badge badge-cyan">Java</span>
                <span class="badge badge-amber">算法</span>
                <span class="badge badge-green">数据库</span>
                <span class="badge badge-rose">Redis</span>
                <span class="badge badge-gray">Spring</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    question = st.text_input("输入你的问题", "", key="rag_question", 
                              placeholder="例如：什么是动态规划？HashMap的底层原理？")
    
    if question:
        with st.spinner("正在检索知识库..."):
            answer = rag_service.answer_with_rag(question)
        
        st.markdown("### 💡 AI回答")
        st.markdown(f"""
        <div class="card card-glow">
            <div class="card-content">{answer}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📚 相关知识点")
        related = rag_service.query(question, top_k=3)
        for doc in related:
            diff_text = doc.get('difficulty', '中等')
            diff_badge = {"简单": "badge-green", "中等": "badge-amber", "困难": "badge-rose"}.get(diff_text, "badge-amber")
            
            with st.expander(f"【{doc['category']}】{doc['question']}"):
                st.markdown(f"<span class='badge {diff_badge}'>{diff_text}</span>", unsafe_allow_html=True)
                st.markdown("---")
                st.write(doc["answer"])

def page_skills():
    st.markdown("""
    <div class="hero-section" style="padding: 1.5rem 0;">
        <h1 style="font-size: 2rem; margin: 0;">📊 技能分析</h1>
        <p style="color: var(--text-secondary); margin-top: 0.5rem;">可视化你的技术能力</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="card card-glow">
            <div class="card-title">
                <span style="font-size: 1.25rem;">🎨</span>
                <span>技能可视化</span>
                <span class="badge badge-green">标签云</span>
            </div>
            <div class="card-content">
                上传简历，AI自动提取技能关键词，生成精美的标签云和技能分布图，
                直观展示你的技术栈和能力分布，帮助你了解自身优势
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title"><span style="font-size: 1.25rem;">📈</span><span>可视化内容</span></div>
            <div class="card-content" style="font-size: 0.85rem;">
                ✓ 技能标签云<br>
                ✓ 技能分布柱状图<br>
                ✓ 技能统计清单
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("上传简历生成技能分析", type="pdf", key="skill_upload")
    
    if uploaded_file is not None:
        file_path = os.path.join(RESUME_UPLOAD_PATH, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("正在分析技能矩阵..."):
            resume_text = resume_service.extract_text_from_pdf(file_path)
            skills = resume_service.extract_skills(resume_text)
        
        if skills:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### ☁️ 技能标签云")
                cloud = visualization_service.generate_skill_cloud(skills)
                if cloud:
                    st.image(io.BytesIO(cloud), use_column_width=True)
            with c2:
                st.markdown("### 📊 技能分布")
                bar = visualization_service.generate_skill_bar_chart(skills)
                if bar:
                    st.image(io.BytesIO(bar), use_column_width=True)
            
            st.markdown("### 📋 技能清单")
            sorted_skills = sorted(skills, key=lambda x: x["count"], reverse=True)
            
            cols = st.columns(4)
            for idx, skill in enumerate(sorted_skills):
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div class="stat-card" style="margin-bottom: 0.75rem;">
                        <div class="stat-number" style="font-size: 1.5rem;">{skill['count']}</div>
                        <div class="stat-label">{skill['skill_name']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("未能提取到技能信息")

def main():
    render_sidebar()
    
    page = st.sidebar.radio(
        "导航",
        ["🏠 首页", "📝 刷题练习", "🎯 模拟面试", "📄 简历优化", 
         "🎯 JD匹配", "🔍 智能问答", "📊 技能分析"],
        label_visibility="collapsed"
    )
    
    if page == "🏠 首页":
        page_dashboard()
    elif page == "📝 刷题练习":
        page_practice()
    elif page == "🎯 模拟面试":
        page_interview()
    elif page == "📄 简历优化":
        page_resume()
    elif page == "🎯 JD匹配":
        page_jd_match()
    elif page == "🔍 智能问答":
        page_rag()
    elif page == "📊 技能分析":
        page_skills()

if __name__ == "__main__":
    main()