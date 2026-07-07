import streamlit as st
import os
import io
from services.rag_service import RAGService
from services.resume_service import ResumeService
from services.visualization_service import VisualizationService
from services.interview_tips_service import InterviewTipsService
from config import RESUME_UPLOAD_PATH

st.set_page_config(
    page_title="AI求职面试助手 | InterviewAI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

* {
    font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
}

code, pre {
    font-family: 'JetBrains Mono', monospace;
}

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0f0f1a 100%);
    min-height: 100vh;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(120, 119, 198, 0.15), transparent),
        radial-gradient(ellipse 60% 40% at 100% 50%, rgba(94, 234, 212, 0.08), transparent),
        radial-gradient(ellipse 60% 40% at 0% 80%, rgba(251, 113, 133, 0.08), transparent);
    pointer-events: none;
    z-index: 0;
}

.block-container {
    position: relative;
    z-index: 1;
    padding-top: 2rem !important;
    max-width: 1400px !important;
}

div[data-testid="stHeader"] {
    background: rgba(10, 10, 15, 0.8) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

div[data-testid="stToolbar"] {
    display: none;
}

h1, h2, h3, h4, h5, h6 {
    color: #f8fafc !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

h1 {
    font-size: 2.75rem !important;
    background: linear-gradient(135deg, #f472b6 0%, #a78bfa 50%, #22d3ee 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem !important;
}

p, span, div, label {
    color: #e2e8f0 !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select,
.stNumberInput input {
    background: rgba(30, 30, 45, 0.6) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 4px rgba(167, 139, 250, 0.15) !important;
    outline: none !important;
}

.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stFileUploader label {
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    margin-bottom: 0.5rem !important;
    text-transform: none !important;
}

.stButton > button {
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    letter-spacing: 0.01em !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    background: linear-gradient(135deg, #a78bfa 0%, #818cf8 100%) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

div[data-testid="stFileUploader"] {
    background: rgba(30, 30, 45, 0.6) !important;
    border: 2px dashed rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: rgba(167, 139, 250, 0.5) !important;
    background: rgba(30, 30, 45, 0.8) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem !important;
    background: rgba(20, 20, 30, 0.7) !important;
    padding: 0.75rem;
    border-radius: 16px;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 2rem;
}

.stTabs [data-baseweb="tab"] {
    height: 48px !important;
    border-radius: 12px !important;
    background: transparent !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 0 1.25rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: none !important;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #e2e8f0 !important;
    background: rgba(255, 255, 255, 0.05) !important;
}

.stTabs [aria-selected="true"] {
    color: white !important;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(99, 102, 241, 0.25) 100%) !important;
    border: 1px solid rgba(167, 139, 250, 0.3) !important;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

div[data-testid="stExpander"] {
    background: rgba(25, 25, 40, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 12px !important;
    margin-bottom: 0.75rem !important;
    overflow: hidden;
    transition: all 0.3s ease !important;
}

div[data-testid="stExpander"]:hover {
    border-color: rgba(167, 139, 250, 0.2) !important;
}

div[data-testid="stExpander"] details summary p {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
}

div[data-testid="stExpander"] details[open] {
    background: rgba(30, 30, 45, 0.7) !important;
}

.stSpinner > div {
    border-color: rgba(139, 92, 246, 0.2) !important;
    border-top-color: #a78bfa !important;
}

div[data-testid="stImage"] {
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
}

.streamlit-expanderHeader {
    font-size: 0.95rem !important;
}

div[data-testid="stMarkdownContainer"] a {
    color: #a78bfa !important;
    text-decoration: none !important;
}

div[data-testid="stMarkdownContainer"] a:hover {
    color: #c4b5fd !important;
}

.card {
    background: rgba(30, 30, 50, 0.5);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 1.75rem;
    margin-bottom: 1.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(167, 139, 250, 0.5), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.card:hover {
    transform: translateY(-2px);
    border-color: rgba(167, 139, 250, 0.2);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}

.card:hover::before {
    opacity: 1;
}

.card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #f8fafc;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.card-content {
    color: #cbd5e1;
    font-size: 0.95rem;
    line-height: 1.7;
}

.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
}

.badge-purple {
    background: rgba(139, 92, 246, 0.15);
    color: #c4b5fd;
    border: 1px solid rgba(139, 92, 246, 0.3);
}

.badge-green {
    background: rgba(34, 197, 94, 0.15);
    color: #86efac;
    border: 1px solid rgba(34, 197, 94, 0.3);
}

.badge-amber {
    background: rgba(245, 158, 11, 0.15);
    color: #fcd34d;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-rose {
    background: rgba(244, 63, 94, 0.15);
    color: #fda4af;
    border: 1px solid rgba(244, 63, 94, 0.3);
}

.badge-cyan {
    background: rgba(6, 182, 212, 0.15);
    color: #67e8f9;
    border: 1px solid rgba(6, 182, 212, 0.3);
}

.hero-section {
    text-align: center;
    padding: 3rem 0 2rem 0;
    position: relative;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 9999px;
    font-size: 0.8rem;
    color: #c4b5fd;
    margin-bottom: 1rem;
    font-weight: 500;
}

.hero-title {
    font-size: 3rem !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
    line-height: 1.2 !important;
}

.hero-subtitle {
    font-size: 1.125rem;
    color: #94a3b8;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

.stat-card {
    background: rgba(30, 30, 50, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    border-color: rgba(167, 139, 250, 0.2);
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f472b6, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.stat-label {
    color: #94a3b8;
    font-size: 0.875rem;
    margin-top: 0.25rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.25rem;
    margin: 2rem 0;
}

.feature-card {
    background: rgba(25, 25, 40, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.feature-card:hover {
    transform: translateY(-4px);
    border-color: rgba(167, 139, 250, 0.3);
    box-shadow: 0 12px 40px rgba(139, 92, 246, 0.15);
}

.feature-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 1rem;
}

.feature-icon-purple {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(99, 102, 241, 0.2));
    border: 1px solid rgba(139, 92, 246, 0.3);
}

.feature-icon-cyan {
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(8, 145, 178, 0.2));
    border: 1px solid rgba(6, 182, 212, 0.3);
}

.feature-icon-rose {
    background: linear-gradient(135deg, rgba(244, 63, 94, 0.2), rgba(225, 29, 72, 0.2));
    border: 1px solid rgba(244, 63, 94, 0.3);
}

.feature-icon-amber {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.2));
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.feature-icon-green {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(22, 163, 74, 0.2));
    border: 1px solid rgba(34, 197, 94, 0.3);
}

.feature-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #f8fafc;
    margin-bottom: 0.5rem;
}

.feature-desc {
    font-size: 0.875rem;
    color: #94a3b8;
    line-height: 1.6;
}

div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

div[data-testid="stAlertContainer"] {
    background: rgba(34, 197, 94, 0.1) !important;
    border: 1px solid rgba(34, 197, 94, 0.2) !important;
    border-radius: 12px !important;
    color: #86efac !important;
}

div[data-testid="stAlertContainer"] p {
    color: #86efac !important;
}

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.03);
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.25);
}

@media (max-width: 768px) {
    h1 {
        font-size: 2rem !important;
    }
    
    .hero-title {
        font-size: 2rem !important;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
    }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

@st.cache_resource
def get_services():
    return RAGService(), ResumeService(), VisualizationService(), InterviewTipsService()

rag_service, resume_service, visualization_service, interview_tips_service = get_services()

def main():
    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">
            <span>✨</span>
            <span>AI-Powered Interview Assistant</span>
        </div>
        <h1 class="hero-title">AI求职面试助手</h1>
        <p class="hero-subtitle">智能简历优化 · 模拟面试训练 · RAG题库问答 · 技能可视化分析<br>让每一次面试都胸有成竹</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem;">
        <div class="stat-card">
            <div class="stat-number">20+</div>
            <div class="stat-label">面试题库</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">AI</div>
            <div class="stat-label">智能优化</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">5大</div>
            <div class="stat-label">核心功能</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">随时练习</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs([
        "  📄  简历优化  ",
        "  🎯  模拟面试  ",
        "  🔍  面试题库  ",
        "  💡  面试技巧  ",
        "  📊  技能分析  "
    ])
    
    with tabs[0]:
        show_resume_optimization()
    
    with tabs[1]:
        show_simulated_interview()
    
    with tabs[2]:
        show_question_bank()
    
    with tabs[3]:
        show_interview_tips()
    
    with tabs[4]:
        show_skill_analysis()

def show_resume_optimization():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>📄</span>
                <span>简历智能优化</span>
                <span class="badge badge-purple" style="margin-left: auto;">AI驱动</span>
            </div>
            <div class="card-content">
                上传你的简历，AI将深入分析内容、提取技能关键词，
                并结合目标岗位提供专业的优化建议，让你的简历脱颖而出。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>⚡</span>
                <span>功能亮点</span>
            </div>
            <div class="card-content" style="font-size: 0.875rem;">
                ✓ 多维度简历分析<br>
                ✓ 目标岗位匹配建议<br>
                ✓ 关键词优化策略<br>
                ✓ 量化成果建议
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("选择简历文件（PDF格式）", type="pdf", key="resume_uploader")
    target_position = st.text_input("目标岗位（选填，帮助提供更精准的建议）", "", key="resume_target_position")
    
    if uploaded_file is not None:
        file_path = os.path.join(RESUME_UPLOAD_PATH, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success("🎉 简历上传成功！开始分析吧")
        
        with st.spinner("正在解析简历内容..."):
            resume_text = resume_service.extract_text_from_pdf(file_path)
            
            with st.expander("📝 查看简历内容", expanded=False):
                st.text_area("", resume_text, height=250, key="resume_content_view")
            
            btn_col1, btn_col2, _ = st.columns([1, 1, 2])
            
            with btn_col1:
                analyze_clicked = st.button("🔍 分析简历", use_container_width=True)
            
            with btn_col2:
                optimize_clicked = st.button("✨ 获取优化建议", use_container_width=True)
            
            if analyze_clicked:
                with st.spinner("AI正在深度分析你的简历..."):
                    analysis = resume_service.analyze_resume(resume_text, target_position)
                
                st.markdown("### 📊 分析报告")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div class="card">
                        <div class="card-title">
                            <span>👤</span>
                            <span>基本信息</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write(analysis.get("basic_info", "暂无分析结果"))
                    
                    st.markdown("""
                    <div class="card">
                        <div class="card-title">
                            <span>🛠</span>
                            <span>技能清单</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    skills = analysis.get("skills", [])
                    if skills:
                        for skill in skills:
                            skill_name = skill.get('skill_name', '')
                            proficiency = skill.get('proficiency', '')
                            st.markdown(f"<span class='badge badge-cyan' style='margin: 0.25rem;'>{skill_name} - {proficiency}</span>", unsafe_allow_html=True)
                    else:
                        st.info("暂未提取到技能信息")
                
                with col2:
                    st.markdown("""
                    <div class="card">
                        <div class="card-title">
                            <span>✨</span>
                            <span>工作经历亮点</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    highlights = analysis.get("experience_highlights", [])
                    if highlights:
                        for i, highlight in enumerate(highlights, 1):
                            st.write(f"{i}. {highlight}")
                    
                    st.markdown("""
                    <div class="card">
                        <div class="card-title">
                            <span>📈</span>
                            <span>待改进点</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    gaps = analysis.get("experience_gaps", [])
                    if gaps:
                        for i, gap in enumerate(gaps, 1):
                            st.write(f"{i}. {gap}")
                
                st.markdown("""
                <div class="card">
                    <div class="card-title">
                        <span>📁</span>
                        <span>项目经验评估</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.write(analysis.get("project_evaluation", ""))
                
                st.markdown("""
                <div class="card">
                    <div class="card-title">
                        <span>💡</span>
                        <span>优化建议</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                suggestions = analysis.get("suggestions", [])
                if suggestions:
                    for i, suggestion in enumerate(suggestions, 1):
                        st.write(f"{i}. {suggestion}")
            
            if optimize_clicked:
                with st.spinner("AI正在生成个性化优化建议..."):
                    suggestions = resume_service.optimize_resume(resume_text, target_position)
                
                st.markdown("### ✨ 优化建议")
                st.markdown(f"""
                <div class="card">
                    <div class="card-content">
                        {suggestions}
                    </div>
                </div>
                """, unsafe_allow_html=True)

def show_simulated_interview():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>🎯</span>
                <span>模拟面试</span>
                <span class="badge badge-rose" style="margin-left: auto;">实战演练</span>
            </div>
            <div class="card-content">
                AI生成真实面试问题，检验你的专业能力和临场反应。
                回答后获得详细的AI点评和改进建议，不断提升面试表现。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>🎲</span>
                <span>题目类型</span>
            </div>
            <div class="card-content" style="font-size: 0.875rem;">
                <span class="badge badge-purple" style="margin: 0.2rem;">技术题</span>
                <span class="badge badge-amber" style="margin: 0.2rem;">行为题</span>
                <span class="badge badge-green" style="margin: 0.2rem;">场景题</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    position = st.text_input("目标岗位（选填，生成更匹配的题目）", "", key="interview_position")
    
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
        st.session_state.answered = False
    
    btn_col1, btn_col2, _ = st.columns([1, 1, 2])
    
    with btn_col1:
        if st.button("🎲 生成面试问题", use_container_width=True):
            with st.spinner("AI正在为你准备面试题..."):
                question = interview_tips_service.generate_practice_question(position)
                st.session_state.current_question = question
                st.session_state.answered = False
    
    with btn_col2:
        if st.button("🔄 换一题", use_container_width=True):
            with st.spinner("AI正在准备新题目..."):
                question = interview_tips_service.generate_practice_question(position)
                st.session_state.current_question = question
                st.session_state.answered = False
    
    if st.session_state.current_question:
        q = st.session_state.current_question
        q_type = q.get('question_type', '技术')
        
        type_badge = "badge-purple" if q_type == "技术" else "badge-amber"
        
        st.markdown(f"""
        <div class="card" style="border-color: rgba(139, 92, 246, 0.3);">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                <span class="badge {type_badge}">{q_type}题</span>
                <span style="color: #64748b; font-size: 0.875rem;">第 1 题</span>
            </div>
            <h3 style="margin: 0; color: #f8fafc; font-size: 1.25rem; line-height: 1.6;">
                {q['question']}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**💬 你的回答**")
        user_answer = st.text_area("", height=180, placeholder="在这里输入你的回答，然后点击下方按钮查看参考答案和AI点评...", key="user_answer_input")
        
        if st.button("📝 提交并查看点评", use_container_width=True):
            st.session_state.answered = True
            
            st.markdown("### 📖 参考答案")
            st.markdown(f"""
            <div class="card">
                <div class="card-content">
                    {q["answer"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if user_answer:
                with st.spinner("AI正在点评你的回答..."):
                    feedback_prompt = f"""请点评以下面试回答：

问题：{q['question']}

求职者回答：{user_answer}

参考答案：{q['answer']}

请从以下几个方面点评：
1. 回答的准确性和完整性
2. 优点和亮点
3. 需要改进的地方
4. 具体的改进建议"""
                    
                    from utils.llm import call_llm
                    feedback = call_llm(feedback_prompt)
                
                st.markdown("### 🤖 AI点评")
                st.markdown(f"""
                <div class="card" style="border-color: rgba(34, 197, 94, 0.2);">
                    <div class="card-content">
                        {feedback}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("💡 试着写下你的回答，会获得更精准的AI点评哦！")

def show_question_bank():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>🔍</span>
                <span>RAG智能问答</span>
                <span class="badge badge-cyan" style="margin-left: auto;">知识库</span>
            </div>
            <div class="card-content">
                基于面试题库的智能检索，输入你想了解的问题，
                AI将结合知识库为你提供最精准的答案和相关知识点。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>📚</span>
                <span>覆盖领域</span>
            </div>
            <div class="card-content" style="font-size: 0.875rem;">
                <span class="badge badge-purple" style="margin: 0.15rem;">Python</span>
                <span class="badge badge-cyan" style="margin: 0.15rem;">算法</span>
                <span class="badge badge-amber" style="margin: 0.15rem;">数据库</span>
                <span class="badge badge-green" style="margin: 0.15rem;">网络</span>
                <span class="badge badge-rose" style="margin: 0.15rem;">系统设计</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    question = st.text_input("输入你的问题", "", key="rag_question_input", placeholder="例如：什么是动态规划？Python的GIL是什么？")
    
    if question:
        with st.spinner("正在检索知识库并生成回答..."):
            answer = rag_service.answer_with_rag(question)
        
        st.markdown("### 💡 AI回答")
        st.markdown(f"""
        <div class="card" style="border-color: rgba(34, 197, 94, 0.2);">
            <div class="card-content">
                {answer}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📚 相关知识点")
        related_docs = rag_service.query(question, top_k=3)
        for doc in related_docs:
            diff_badge = {
                "简单": "badge-green",
                "中等": "badge-amber",
                "困难": "badge-rose"
            }.get(doc['difficulty'], "badge-purple")
            
            with st.expander(f"【{doc['category']}】 {doc['question']}"):
                st.markdown(f"<span class='badge {diff_badge}'>难度：{doc['difficulty']}</span>", unsafe_allow_html=True)
                st.markdown("---")
                st.write(doc["answer"])
    
    st.markdown("### 📝 按分类浏览")
    
    categories = ["Python", "算法", "数据库", "网络", "操作系统", "系统设计", "行为面试"]
    selected_category = st.selectbox("选择分类", categories, key="category_selector")
    
    if st.button("📂 查看该分类问题", use_container_width=True):
        questions = rag_service.collection.get(
            where={"category": selected_category},
            include=["documents", "metadatas"]
        )
        
        if questions["documents"]:
            st.success(f"找到 {len(questions['documents'])} 道{selected_category}面试题")
            
            for doc, meta in zip(questions["documents"], questions["metadatas"]):
                parts = doc.split("\n")
                q_text = parts[0].replace("问题：", "")
                a_text = parts[1].replace("答案：", "") if len(parts) > 1 else ""
                
                diff_badge = {
                    "简单": "badge-green",
                    "中等": "badge-amber",
                    "困难": "badge-rose"
                }.get(meta['difficulty'], "badge-purple")
                
                with st.expander(q_text):
                    st.markdown(f"<span class='badge {diff_badge}'>难度：{meta['difficulty']}</span>", unsafe_allow_html=True)
                    st.markdown("---")
                    st.write(a_text)
        else:
            st.info("暂无该分类的问题")

def show_interview_tips():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>💡</span>
                <span>面试技巧推荐</span>
                <span class="badge badge-amber" style="margin-left: auto;">干货满满</span>
            </div>
            <div class="card-content">
                根据你的目标岗位，AI将为你推荐最实用的面试技巧、
                常见问题和注意事项，助你在面试中表现更加出色。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>🎯</span>
                <span>涵盖模块</span>
            </div>
            <div class="card-content" style="font-size: 0.875rem;">
                ✓ 技术准备指南<br>
                ✓ 简历优化策略<br>
                ✓ 行为面试攻略<br>
                ✓ 薪资谈判技巧
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    position = st.text_input("输入目标岗位", "", key="tips_position", placeholder="例如：Python后端工程师、前端开发工程师...")
    
    if position:
        with st.spinner("AI正在为你定制面试技巧..."):
            tips = interview_tips_service.get_tips_by_position(position)
        
        st.markdown("### 📋 专属面试攻略")
        st.markdown(f"""
        <div class="card">
            <div class="card-content">
                {tips}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 常见行为面试问题")
    
    if st.button("📝 获取行为面试问题库", use_container_width=True):
        with st.spinner("正在整理行为面试问题..."):
            questions = interview_tips_service.get_behavior_questions(position)
        
        if questions:
            for i, q in enumerate(questions, 1):
                with st.expander(f"{i}. {q['question']}"):
                    st.markdown(f"""
                    <div class="card" style="margin-bottom: 0;">
                        <div class="card-title" style="font-size: 0.95rem;">
                            <span>💡</span>
                            <span>回答要点</span>
                        </div>
                        <div class="card-content">
                            {q['answer_tips']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

def show_skill_analysis():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>📊</span>
                <span>技能可视化分析</span>
                <span class="badge badge-green" style="margin-left: auto;">标签云</span>
            </div>
            <div class="card-content">
                上传简历，AI自动提取技能关键词并生成精美的标签云和分布图，
                让你直观了解自己的技能矩阵和优势领域。
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-title">
                <span>🎨</span>
                <span>可视化形式</span>
            </div>
            <div class="card-content" style="font-size: 0.875rem;">
                <span class="badge badge-purple" style="margin: 0.15rem;">标签云</span>
                <span class="badge badge-cyan" style="margin: 0.15rem;">柱状图</span>
                <span class="badge badge-amber" style="margin: 0.15rem;">技能清单</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("上传简历生成技能分析图", type="pdf", key="skill_analysis_upload")
    
    if uploaded_file is not None:
        file_path = os.path.join(RESUME_UPLOAD_PATH, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("AI正在分析你的技能矩阵..."):
            resume_text = resume_service.extract_text_from_pdf(file_path)
            skills = resume_service.extract_skills(resume_text)
            
            if skills:
                st.markdown("### 🎨 技能标签云")
                cloud_image = visualization_service.generate_skill_cloud(skills)
                if cloud_image:
                    st.image(io.BytesIO(cloud_image), use_column_width=True)
                else:
                    st.info("标签云生成中...显示技能列表")
                
                st.markdown("### 📈 技能分布")
                bar_image = visualization_service.generate_skill_bar_chart(skills)
                if bar_image:
                    st.image(io.BytesIO(bar_image), use_column_width=True)
                
                st.markdown("### 📋 技能清单")
                
                sorted_skills = sorted(skills, key=lambda x: x["count"], reverse=True)
                
                cols = st.columns(3)
                for idx, skill in enumerate(sorted_skills):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        st.markdown(f"""
                        <div class="stat-card" style="margin-bottom: 0.75rem;">
                            <div class="stat-number" style="font-size: 1.25rem;">{skill['count']}</div>
                            <div class="stat-label">{skill['skill_name']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("未能提取到技能信息，请确保简历内容清晰可读")

if __name__ == "__main__":
    main()
