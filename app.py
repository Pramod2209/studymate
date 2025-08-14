import streamlit as st
import time
import json
import re
import os
from dotenv import load_dotenv

# Update import paths to match the project structure
from pdf_processor import PDFProcessor
from ai_services import AIServices
from animations import load_css, create_animated_header, show_loading_animation

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="StudyMate AI - PDF Analysis",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Initialize services with error handling
@st.cache_resource
def initialize_services():
    try:
        return PDFProcessor(), AIServices()
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.stop()

# Initialize session state with default values
def init_session_state():
    defaults = {
        'pdf_content': "",
        'pdf_filename': "",
        'chat_history': [],
        'processed_content': {},
        'current_page': "upload"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize app
init_session_state()

try:
    pdf_processor, ai_services = initialize_services()
except Exception as e:
    st.error(f"Application initialization failed: {str(e)}")
    st.stop()

def apply_styling():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .premium-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .premium-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="20" cy="80" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        pointer-events: none;
    }
    
    .success-notification {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .hero-section {
        text-align: center;
        color: black;
        margin-bottom: 3rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: #000000;
        margin-bottom: 1rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        opacity: 0.95;
        font-weight: 400;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .hero-description {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        opacity: 0.8;
        font-weight: 300;
        max-width: 600px;
        margin: 0 auto;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin-top: 3rem;
        position: relative;
        z-index: 1;
    }
    
    .feature-card {
        background: white;
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        border: 1px solid rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 25px 60px rgba(0,0,0,0.15);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .feature-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 1rem;
        letter-spacing: -0.025em;
    }
    
    .feature-description {
        font-family: 'Inter', sans-serif;
        color: #6b7280;
        font-size: 1rem;
        line-height: 1.6;
        font-weight: 400;
        max-width: 280px;
        margin: 0 auto;
    }
    
    .floating-elements {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
        overflow: hidden;
    }
    
    .floating-circle {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        animation: float 6s ease-in-out infinite;
    }
    
    .floating-circle:nth-child(1) {
        width: 80px;
        height: 80px;
        top: 10%;
        left: 10%;
        animation-delay: 0s;
    }
    
    .floating-circle:nth-child(2) {
        width: 60px;
        height: 60px;
        top: 20%;
        right: 15%;
        animation-delay: 2s;
    }
    
    .floating-circle:nth-child(3) {
        width: 40px;
        height: 40px;
        bottom: 20%;
        left: 20%;
        animation-delay: 4s;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    @media (max-width: 768px) {
        .features-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
        
        .premium-container {
            padding: 2rem 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def show_action_menu():
    """Show action menu with highly attractive, modern design"""
    
    # Enhanced CSS for premium, attractive design
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .premium-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 25px;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .premium-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="20" cy="80" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        pointer-events: none;
    }
    
    .success-notification {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .hero-section {
        text-align: center;
        color: black;
        margin-bottom: 3rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: #000000;
        margin-bottom: 1rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.4rem;
        opacity: 0.95;
        font-weight: 400;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .hero-description {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        opacity: 0.8;
        font-weight: 300;
        max-width: 600px;
        margin: 0 auto;
    }
    
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 2rem;
        margin-top: 3rem;
        position: relative;
        z-index: 1;
    }
    
    .feature-card {
        background: white;
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        border: 1px solid rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: left 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 25px 60px rgba(0,0,0,0.15);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .feature-icon {
        font-size: 4rem;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .feature-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 1rem;
        letter-spacing: -0.025em;
    }
    
    .feature-description {
        font-family: 'Inter', sans-serif;
        color: #6b7280;
        font-size: 1rem;
        line-height: 1.6;
        font-weight: 400;
        max-width: 280px;
        margin: 0 auto;
    }
    
    .floating-elements {
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
        overflow: hidden;
    }
    
    .floating-circle {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        animation: float 6s ease-in-out infinite;
    }
    
    .floating-circle:nth-child(1) {
        width: 80px;
        height: 80px;
        top: 10%;
        left: 10%;
        animation-delay: 0s;
    }
    
    .floating-circle:nth-child(2) {
        width: 60px;
        height: 60px;
        top: 20%;
        right: 15%;
        animation-delay: 2s;
    }
    
    .floating-circle:nth-child(3) {
        width: 40px;
        height: 40px;
        bottom: 20%;
        left: 20%;
        animation-delay: 4s;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    @media (max-width: 768px) {
        .features-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .hero-title {
            font-size: 2.5rem;
        }
        
        .premium-container {
            padding: 2rem 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Success notification
    st.markdown(f"""
    <div class="success-notification">
        ✨ Document "{st.session_state.pdf_filename}" uploaded successfully! Choose an action below to get started:
    </div>
    """, unsafe_allow_html=True)
    
    # Main premium container
    st.markdown('<div class="premium-container">', unsafe_allow_html=True)
    
    # Floating background elements
    st.markdown("""
    <div class="floating-elements">
        <div class="floating-circle"></div>
        <div class="floating-circle"></div>
        <div class="floating-circle"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">🎓 StudyMate AI</div>
        <div class="hero-subtitle">Your AI-Powered PDF Study Assistant</div>
        <div class="hero-description">Unlock the power of intelligent document analysis with advanced AI capabilities</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features grid
    st.markdown('<div class="features-grid">', unsafe_allow_html=True)
    
    # Create feature cards using columns for better control
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # PDF Q&A Card
        if st.button("", key="qa_card", help="Ask questions about your PDF content"):
            st.session_state.current_page = "qa"
            st.rerun()
        
        st.markdown("""
        <div class="feature-card" onclick="document.querySelector('[data-testid=\"stButton\"][title=\"Ask questions about your PDF content\"] button').click()">
            <div class="feature-icon">❓</div>
            <div class="feature-title">PDF Q&A</div>
            <div class="feature-description">Ask intelligent questions about your PDF content and get detailed answers</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate Quiz Card
        if st.button("", key="test_card", help="Create quizzes from PDF content"):
            st.session_state.current_page = "test"
            st.rerun()
            
        st.markdown("""
        <div class="feature-card" onclick="document.querySelector('[data-testid=\"stButton\"][title=\"Create quizzes from PDF content\"] button').click()">
            <div class="feature-icon">📝</div>
            <div class="feature-title">Generate Quiz</div>
            <div class="feature-description">Create custom quizzes and practice tests from your PDF content</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Summarization Card
        if st.button("", key="summary_card", help="Get concise summaries of your PDF"):
            st.session_state.current_page = "summarize"
            st.rerun()
            
        st.markdown("""
        <div class="feature-card" onclick="document.querySelector('[data-testid=\"stButton\"][title=\"Get concise summaries of your PDF\"] button').click()">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Smart Summarization</div>
            <div class="feature-description">Get concise, intelligent summaries of your PDF documents</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Study Suggestions Card
        if st.button("", key="topics_card", help="Get related topics to explore"):
            st.session_state.current_page = "topics"
            st.rerun()
            
        st.markdown("""
        <div class="feature-card" onclick="document.querySelector('[data-testid=\"stButton\"][title=\"Get related topics to explore\"] button').click()">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Study Suggestions</div>
            <div class="feature-description">Discover related topics and study recommendations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Explain Concepts Card
        if st.button("", key="explain_card", help="Get detailed explanations with examples"):
            st.session_state.current_page = "qa"
            st.rerun()
            
        st.markdown("""
        <div class="feature-card" onclick="document.querySelector('[data-testid=\"stButton\"][title=\"Get detailed explanations with examples\"] button').click()">
            <div class="feature-icon">💡</div>
            <div class="feature-title">Explain Concepts</div>
            <div class="feature-description">Get detailed explanations with examples and context</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Translation Card
        if st.button("", key="translate_card", help="Translate PDF content to other languages"):
            st.session_state.current_page = "translate"
            st.rerun()
            
        st.markdown("""
        <div class="feature-card" onclick="document.querySelector('[data-testid=\"stButton\"][title=\"Translate PDF content to other languages\"] button').click()">
            <div class="feature-icon">🌐</div>
            <div class="feature-title">Multi-Language Translation</div>
            <div class="feature-description">Translate PDF content to multiple languages instantly</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close features-grid
    st.markdown('</div>', unsafe_allow_html=True)  # Close premium-container

def create_feature_card(key, help_text, icon, title, description, page_name):
    if st.button("", key=key, help=help_text):
        st.session_state.current_page = page_name
        st.rerun()

    # The 'primary' class is removed from the div to ensure uniform color
    st.markdown(f"""
    <div class="feature-card" onclick="document.querySelector('[data-testid=\"stButton\"][title=\"{help_text}\"] button').click()">
        <div class="feature-icon">{icon}</div>
        <div class="feature-title">{title}</div>
        <div class="feature-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)

def handle_translation():
    st.markdown("## 🌍 Multi-Language Translation")
    st.markdown("Translate your document content to different languages")

    if st.button("← Back to Actions", key="back_translation"):
        st.session_state.current_page = "main"
        # Clear previous translation results when going back
        if 'translated_text' in st.session_state:
            del st.session_state.translated_text
        st.rerun()

    if not st.session_state.get("pdf_content"):
        st.warning("⚠️ Please upload a PDF first!")
        return

    st.markdown("#### Select a language to translate to:")
    languages = ["Spanish", "French", "German", "Chinese", "Japanese", "Russian", "Arabic", "Portuguese", "Hindi"]
    
    # Create a grid of language buttons
    cols = st.columns(4)
    for i, lang in enumerate(languages):
        with cols[i % 4]:
            if st.button(lang, key=f"lang_{lang}", use_container_width=True):
                with st.spinner(f"Translating to {lang}, please wait..."):
                    full_text = st.session_state.get("pdf_content", "")
                    if full_text:
                        ai = AIServices()
                        translated_content = ai.translate(full_text, lang)
                        st.session_state.translated_text = translated_content
                        st.session_state.translated_lang = lang
                    else:
                        st.session_state.translated_text = "Error: PDF content not found."
                st.rerun()

    if "translated_text" in st.session_state:
        st.text_area("Translated Content", st.session_state.translated_text, height=300)
        if st.session_state.translated_text and "error" not in st.session_state.translated_text.lower() and len(st.session_state.translated_text) > 50:
            st.download_button(
                label="📥 Download Translation",
                data=st.session_state.translated_text.encode('utf-8'),
                file_name=f"translation_{st.session_state.get('translated_lang')}.txt",
                mime="text/plain"
            )
        else:
            st.error("Translation failed or the content is too short. Cannot download.")

def main():
    apply_styling()
    # Animated header
    create_animated_header("📚 StudyMate AI", "Your intelligent PDF analysis companion powered by IBM Granite")
    
    # Initialize current page if not set
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "upload"
    
    # Simplified sidebar - just show document status
    with st.sidebar:
        st.markdown("## 📋 Document Status")
        
        if st.session_state.pdf_content:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                font-weight: 500;
                box-shadow: 0 4px 15px rgba(82, 196, 26, 0.3);
                margin-bottom: 1rem;
            '>
                ✅ Document Ready<br>
                <strong>{st.session_state.pdf_filename}</strong><br>
                <small>📊 {len(st.session_state.pdf_content)} characters</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Button to change document
            if st.button("📤 Upload New Document", use_container_width=True):
                st.session_state.current_page = "upload"
                st.rerun()
                
            # Add chat history section
            st.markdown("## 💬 Chat History")
            
            # Add custom CSS for chat history
            st.markdown("""
            <style>
            .chat-history {
                max-height: 400px;
                overflow-y: auto;
                padding: 10px;
                border-radius: 10px;
                background-color: #f8f9fa;
                margin-top: 10px;
            }
            .chat-message {
                background: white;
                padding: 10px 15px;
                border-radius: 10px;
                margin-bottom: 10px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .chat-question {
                font-weight: 500;
                color: #1a73e8;
                margin-bottom: 5px;
                font-size: 0.9em;
            }
            .chat-answer {
                color: #333;
                font-size: 0.85em;
                white-space: pre-wrap;
            }
            .no-chat {
                text-align: center;
                color: #666;
                font-style: italic;
                padding: 20px 0;
                font-size: 0.9em;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.session_state.chat_history:
                with st.container():
                    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
                    
                    # Show only the last 5 messages to prevent clutter
                    for msg in st.session_state.chat_history[-5:]:
                        st.markdown(f'''
                        <div class="chat-message">
                            <div class="chat-question">Q: {msg['question']}</div>
                            <div class="chat-answer">A: {msg['answer'][:100]}{'...' if len(msg['answer']) > 100 else ''}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add a button to clear history
                    if st.button("🗑️ Clear History", use_container_width=True, key="clear_history"):
                        st.session_state.chat_history = []
                        st.rerun()
            else:
                st.markdown('<div class="no-chat">No chat history yet</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, #FF8C42 0%, #FFD23F 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                font-weight: 500;
                box-shadow: 0 4px 15px rgba(255, 140, 66, 0.3);
            '>
                📄 No document uploaded<br>
                <small>Upload a PDF to begin</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Main content area
    if not st.session_state.pdf_content or st.session_state.current_page == "upload":
        handle_pdf_upload()
    elif st.session_state.current_page == "main":
        # Show action buttons popup/menu after PDF is uploaded
        show_action_menu()
    else:
        # Handle the selected action
        if st.session_state.current_page == "summarize":
            handle_summarization()
        elif st.session_state.current_page == "translate":
            handle_translation()
        elif st.session_state.current_page == "topics":
            handle_topic_extraction()
        elif st.session_state.current_page == "qa":
            handle_qa_session()
        elif st.session_state.current_page == "test":
            handle_test_generation()

def handle_pdf_upload():
    st.markdown("## 📤 Upload Your Document")
    st.markdown("Upload academic papers, textbooks, research documents, or any study materials")
    
    # Animated upload area
    st.markdown("""
    <div class="upload-area">
        <div class="upload-animation">
            📄 → 🧠 → ✨
        </div>
        <h3 style="color: var(--medium-text); margin: 1rem 0;">Drag and drop your PDF here</h3>
        <p style="color: var(--light-text); font-size: 0.9rem;">Supported format: PDF • Max size: 200MB</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload academic papers, textbooks, research papers, lecture notes, or any study materials",
        key="pdf_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        with st.spinner("🔄 Processing PDF..."):
            try:
                # Animate processing
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("📖 Extracting text...")
                progress_bar.progress(25)
                
                text_content = pdf_processor.extract_text(uploaded_file)
                
                status_text.text("🧠 Processing content...")
                progress_bar.progress(75)
                time.sleep(0.5)  # Smooth animation
                
                st.session_state.pdf_content = text_content
                st.session_state.pdf_filename = uploaded_file.name
                st.session_state.current_page = "main"  # Switch to main action menu
                
                status_text.text("✅ Processing complete!")
                progress_bar.progress(100)
                
                time.sleep(1)
                status_text.empty()
                progress_bar.empty()
                
                # Show success message and rerun to show action menu
                st.success("🎉 Document processed successfully! Action menu will appear below.")
                time.sleep(1)
                st.rerun()
                
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 20px;
                    text-align: center;
                    font-weight: 500;
                    box-shadow: 0 8px 25px rgba(82, 196, 26, 0.3);
                    margin: 1rem 0;
                '>
                    🎉 Successfully processed: <strong>{uploaded_file.name}</strong><br>
                    <small>📊 {len(text_content)} characters • ~{len(text_content.split())} words</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Preview
                with st.expander("👀 Document Preview", expanded=False):
                    st.markdown("**Content Preview:**")
                    preview_text = text_content[:1200] + "..." if len(text_content) > 1200 else text_content
                    st.text_area("Document Preview", preview_text, height=200, disabled=True, label_visibility="collapsed")
                
            except Exception as e:
                st.error(f"❌ Error processing PDF: {str(e)}")

def handle_summarization():
    st.markdown("## 📄 Document Summarization")
    st.markdown("Generate intelligent summaries of your uploaded document")
    
    # Back button
    if st.button("← Back to Actions", key="back_summary"):
        st.session_state.current_page = "main"
        st.rerun()
    
    if not st.session_state.pdf_content:
        st.warning("⚠️ Please upload a PDF first!")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        summary_length = st.select_slider(
            "Summary Length",
            options=["Brief", "Medium", "Detailed"],
            value="Medium",
            key="summary_length"
        )
    
    with col2:
        summary_style = st.selectbox(
            "Summary Style",
            ["Academic", "Simple", "Bullet Points"],
            key="summary_style"
        )
    
    if st.button("🚀 Generate Summary", use_container_width=True):
        with st.spinner("🤖 AI is analyzing your document..."):
            show_loading_animation("Generating summary")
            
            try:
                summary = ai_services.summarize_content(
                    st.session_state.pdf_content,
                    length=summary_length,
                    style=summary_style
                )
                
                # Animated result display
                st.markdown("### ✨ Summary Generated!")
                
                with st.container():
                    st.markdown("""
                    <div class="result-card">
                    """, unsafe_allow_html=True)
                    
                    st.markdown(summary)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Download option
                st.download_button(
                    label="📥 Download Summary",
                    data=summary,
                    file_name=f"summary_{st.session_state.pdf_filename}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"❌ Error generating summary: {str(e)}")

def handle_topic_extraction():
    st.markdown("## 🏷️ Key Topic Extraction")
    st.markdown("Identify and analyze the main topics and themes in your document")
    
    # Back button
    if st.button("← Back to Actions", key="back_topics"):
        st.session_state.current_page = "main"
        st.rerun()
    
    if not st.session_state.pdf_content:
        st.warning("⚠️ Please upload a PDF first!")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_topics = st.slider("Number of Topics", 3, 15, 8, key="num_topics")
    
    with col2:
        topic_type = st.selectbox(
            "Topic Type",
            ["Main Themes", "Key Concepts", "Technical Terms", "Study Points"],
            key="topic_type"
        )
    
    if st.button("🔍 Extract Topics", use_container_width=True):
        with st.spinner("🧠 Analyzing document structure..."):
            show_loading_animation("Extracting topics")
            
            try:
                topics = ai_services.extract_topics(
                    st.session_state.pdf_content,
                    num_topics=num_topics,
                    topic_type=topic_type
                )
                
                st.markdown("### 🎯 Topics Extracted!")
                
                # Display topics with animations
                for i, topic in enumerate(topics, 1):
                    with st.expander(f"📌 Topic {i}: {topic['title']}", expanded=True):
                        st.markdown(f"**Description:** {topic['description']}")
                        st.markdown(f"**Key Points:**")
                        for point in topic['key_points']:
                            st.markdown(f"• {point}")
                        st.markdown(f"**Relevance:** {topic['relevance']}")
                
                # Export options
                col1, col2 = st.columns(2)
                
                with col1:
                    topics_text = "\n".join([f"{i}. {topic['title']}\n{topic['description']}\nKey Points:\n" + 
                                           "\n".join([f"- {point}" for point in topic['key_points']]) + f"\nRelevance: {topic['relevance']}\n"
                                           for i, topic in enumerate(topics, 1)])
                    
                    st.download_button(
                        label="📥 Download Topics (TXT)",
                        data=topics_text,
                        file_name=f"topics_{st.session_state.pdf_filename}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    topics_json = json.dumps(topics, indent=2)
                    st.download_button(
                        label="📥 Download Topics (JSON)",
                        data=topics_json,
                        file_name=f"topics_{st.session_state.pdf_filename}.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"❌ Error extracting topics: {str(e)}")

def handle_qa_session():
    st.markdown("## ❓ Interactive Q&A Session")
    st.markdown("Ask questions about your document and get intelligent answers")
    
    # Back button
    if st.button("← Back to Actions", key="back_qa"):
        st.session_state.current_page = "main"
        st.rerun()
    
    if not st.session_state.pdf_content:
        st.warning("⚠️ Please upload a PDF first!")
        return
    
    # Quick question suggestions
    st.markdown("### 💡 Quick Questions")
    quick_questions = [
        "What is the main topic of this document?",
        "What are the key conclusions?",
        "Can you explain the methodology used?",
        "What are the important definitions mentioned?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(question, key=f"quick_q_{i}", use_container_width=True):
                process_question(question)
    
    # Custom question input
    st.markdown("### 🤔 Ask Your Own Question")
    
    with st.form("question_form"):
        user_question = st.text_area(
            "Your Question:",
            placeholder="Ask anything about the PDF content...",
            height=100,
            key="user_question"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("🚀 Ask Question", use_container_width=True)
    
    if submit_button and user_question:
        process_question(user_question)

def process_question(question):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Analyzing document and generating answer..."):
            full_text = st.session_state.get("pdf_content", "")
            if full_text:
                ai = AIServices()
                response = ai.answer_question(full_text, question)
                message_placeholder.markdown(response)
            else:
                response = "I can't answer questions without a PDF document. Please upload one first."
                message_placeholder.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

def handle_test_generation():
    st.markdown("## 📝 Practice Test Generator")
    st.markdown("Create custom test questions based on your document content")
    
    # Back button
    if st.button("← Back to Actions", key="back_test"):
        st.session_state.current_page = "main"
        st.rerun()
    
    if not st.session_state.pdf_content:
        st.warning("⚠️ Please upload a PDF first!")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        question_count = st.selectbox(
            "Number of Questions",
            [5, 10, 15, 20],
            key="question_count"
        )
    
    with col2:
        question_type = st.selectbox(
            "Question Type",
            ["Multiple Choice", "Short Answer", "Essay", "Mixed"],
            key="question_type"
        )
    
    with col3:
        difficulty = st.selectbox(
            "Difficulty Level",
            ["Easy", "Medium", "Hard", "Mixed"],
            key="difficulty"
        )
    
    if st.button("📝 Generate Test", use_container_width=True):
        with st.spinner("🎓 Creating your personalized test..."):
            show_loading_animation("Generating test questions")
            
            try:
                test_questions = ai_services.generate_test(
                    st.session_state.pdf_content,
                    question_count=question_count,
                    question_type=question_type,
                    difficulty=difficulty
                )
                
                st.markdown("### 🎯 Test Generated!")
                st.markdown(f"**{question_count} {difficulty.lower()} {question_type.lower()} questions**")
                
                # Display questions
                for i, question in enumerate(test_questions, 1):
                    with st.expander(f"Question {i}", expanded=False):
                        st.markdown(f"**{question['question']}**")
                        
                        if question['type'] == 'multiple_choice' and 'options' in question:
                            for j, option in enumerate(question['options'], 1):
                                st.markdown(f"{chr(64+j)}. {option}")
                            st.markdown(f"**Correct Answer:** {question.get('correct_answer', 'Not specified')}")
                        
                        if 'explanation' in question:
                            st.markdown(f"**Explanation:** {question['explanation']}")
                
                # Export options
                col1, col2 = st.columns(2)
                
                with col1:
                    # Format for text export
                    test_text = f"Test Questions - {st.session_state.pdf_filename}\n"
                    test_text += "="*50 + "\n\n"
                    
                    for i, question in enumerate(test_questions, 1):
                        test_text += f"Question {i}: {question['question']}\n"
                        if question['type'] == 'multiple_choice' and 'options' in question:
                            for j, option in enumerate(question['options'], 1):
                                test_text += f"{chr(64+j)}. {option}\n"
                            test_text += f"Correct Answer: {question.get('correct_answer', 'Not specified')}\n"
                        if 'explanation' in question:
                            test_text += f"Explanation: {question['explanation']}\n"
                        test_text += "\n" + "-"*30 + "\n\n"
                    
                    st.download_button(
                        label="📥 Download Test (TXT)",
                        data=test_text,
                        file_name=f"test_{st.session_state.pdf_filename}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    test_json = json.dumps(test_questions, indent=2)
                    st.download_button(
                        label="📥 Download Test (JSON)",
                        data=test_json,
                        file_name=f"test_{st.session_state.pdf_filename}.json",
                        mime="application/json"
                    )
                
            except Exception as e:
                st.error(f"❌ Error generating test: {str(e)}")

if __name__ == "__main__":
    main()