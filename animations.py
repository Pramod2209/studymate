import streamlit as st
import time

def load_css():
    """Load custom CSS for animations and styling"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --primary-orange: #FF8C42;
        --secondary-yellow: #FFD23F;
        --warm-orange: #FF6B35;
        --light-orange: #FFF4E6;
        --dark-text: #2C3E50;
        --medium-text: #5A6C7D;
        --light-text: #8B9DC3;
        --white: #FFFFFF;
        --light-bg: #FAFBFC;
        --shadow-light: rgba(255, 140, 66, 0.1);
        --shadow-medium: rgba(255, 140, 66, 0.2);
        --shadow-strong: rgba(255, 140, 66, 0.3);
    }
    
    /* Global font and body styling */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, #FFF8F0 0%, #FFF4E6 100%);
        color: var(--dark-text);
    }
    
    /* Main animations and styling */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Header animations */
    .animated-header {
        animation: fadeInUp 1s ease-out;
        text-align: center;
        padding: 3rem 2rem 2rem 2rem;
        background: linear-gradient(135deg, var(--primary-orange) 0%, var(--warm-orange) 100%);
        border-radius: 24px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 20px 40px var(--shadow-medium);
        position: relative;
        overflow: hidden;
    }
    
    .animated-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    .animated-header h1 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 3.5rem;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .animated-subtitle {
        animation: fadeInUp 1.2s ease-out;
        opacity: 0.95;
        margin-top: 1rem;
        font-weight: 400;
        font-size: 1.3rem;
        position: relative;
        z-index: 1;
    }
    
    /* Upload area styling */
    .upload-area {
        border: 3px dashed var(--primary-orange);
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 2rem 0;
        background: linear-gradient(135deg, var(--light-orange) 0%, rgba(255, 212, 63, 0.1) 100%);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .upload-area::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 140, 66, 0.1), transparent);
        transition: left 0.6s;
    }
    
    .upload-area:hover {
        border-color: var(--warm-orange);
        background: linear-gradient(135deg, rgba(255, 212, 63, 0.15) 0%, var(--light-orange) 100%);
        transform: translateY(-4px);
        box-shadow: 0 15px 35px var(--shadow-medium);
    }
    
    .upload-area:hover::before {
        left: 100%;
    }
    
    .upload-animation {
        font-size: 3rem;
        animation: pulse 2s infinite;
        margin-bottom: 1.5rem;
        filter: drop-shadow(0 2px 8px var(--shadow-light));
    }
    
    /* Result cards */
    .result-card {
        background: linear-gradient(135deg, var(--white) 0%, var(--light-orange) 20%, var(--white) 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        animation: fadeInUp 0.6s ease-out;
        box-shadow: 0 10px 40px var(--shadow-light);
        border: 1px solid rgba(255, 140, 66, 0.15);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-orange) 0%, var(--secondary-yellow) 100%);
        border-radius: 20px 20px 0 0;
    }
    
    .qa-card {
        background: linear-gradient(135deg, var(--secondary-yellow) 0%, var(--primary-orange) 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        animation: slideIn 0.6s ease-out;
        box-shadow: 0 15px 40px var(--shadow-medium);
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .qa-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 8s ease-in-out infinite;
    }
    
    /* Action Menu Styling */
    .action-menu {
        background: var(--white);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 40px var(--shadow-light);
        border: 1px solid rgba(255, 140, 66, 0.1);
    }
    
    .action-button {
        background: var(--white);
        border: 2px solid rgba(255, 140, 66, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        text-align: left;
        transition: all 0.3s ease;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 2px 8px rgba(255, 140, 66, 0.1);
    }
    
    .action-button:hover {
        background: var(--light-orange);
        border-color: var(--primary-orange);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px var(--shadow-medium);
    }
    
    .action-button-icon {
        font-size: 1.5rem;
        width: 40px;
        text-align: center;
    }
    
    .action-button-text {
        flex: 1;
    }
    
    .action-button-title {
        font-weight: 600;
        color: var(--dark-text);
        margin: 0;
        font-size: 1.1rem;
    }
    
    .action-button-desc {
        color: var(--medium-text);
        margin: 0.25rem 0 0 0;
        font-size: 0.9rem;
    }

    /* Button animations */
    .stButton button {
        background: linear-gradient(135deg, var(--primary-orange) 0%, var(--warm-orange) 100%);
        border: none;
        border-radius: 30px;
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.75rem 2rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 20px var(--shadow-light);
        position: relative;
        overflow: hidden;
        text-transform: none;
        letter-spacing: 0.5px;
        min-height: 48px;
    }
    
    .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 30px var(--shadow-medium);
        background: linear-gradient(135deg, var(--warm-orange) 0%, var(--primary-orange) 100%);
    }
    
    .stButton button:hover::before {
        left: 100%;
    }
    
    .stButton button:active {
        transform: translateY(-1px) scale(0.98);
    }
    
    /* Loading animations */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 3rem;
        flex-direction: column;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(255, 140, 66, 0.2);
        border-top: 4px solid var(--primary-orange);
        border-radius: 50%;
        animation: rotate 1s linear infinite;
        margin-bottom: 1rem;
        filter: drop-shadow(0 2px 8px var(--shadow-light));
    }
    
    .loading-text {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: var(--medium-text);
        font-weight: 500;
        text-align: center;
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .stSidebar > div {
        background: linear-gradient(180deg, var(--white) 0%, var(--light-orange) 100%);
        border-right: 1px solid rgba(255, 140, 66, 0.1);
    }
    
    .stSidebar .stRadio > div {
        background: var(--white);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 140, 66, 0.1);
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px var(--shadow-light);
    }
    
    .stSidebar .stRadio > div:hover {
        background: var(--light-orange);
        transform: translateX(5px);
        box-shadow: 0 4px 15px var(--shadow-medium);
    }
    
    .stSidebar .stMarkdown h2 {
        color: var(--dark-text);
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.5rem;
    }
    
    .stSidebar label {
        color: var(--medium-text);
        font-weight: 500;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-orange) 0%, var(--secondary-yellow) 100%);
        border-radius: 10px;
    }
    
    .stProgress {
        background-color: rgba(255, 140, 66, 0.1);
        border-radius: 10px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, var(--light-orange) 0%, var(--white) 100%);
        border-radius: 15px;
        border: 1px solid rgba(255, 140, 66, 0.2);
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(90deg, var(--secondary-yellow) 0%, var(--light-orange) 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px var(--shadow-light);
    }
    
    .streamlit-expanderContent {
        background: var(--white);
        border: 1px solid rgba(255, 140, 66, 0.1);
        border-radius: 0 0 15px 15px;
        padding: 1rem;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background: linear-gradient(90deg, #52C41A 0%, #73D13D 100%);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(82, 196, 26, 0.3);
    }
    
    .stError {
        background: linear-gradient(90deg, #FF4D4F 0%, #FF7875 100%);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(255, 77, 79, 0.3);
    }
    
    .stWarning {
        background: linear-gradient(90deg, var(--secondary-yellow) 0%, var(--primary-orange) 100%);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 15px var(--shadow-medium);
    }
    
    .stInfo {
        background: linear-gradient(90deg, #1890FF 0%, #40A9FF 100%);
        border: none;
        border-radius: 15px;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(24, 144, 255, 0.3);
    }
    
    /* Custom animation classes */
    .bounce-in {
        animation: bounceIn 0.6s ease-out;
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    .slide-up {
        animation: slideUp 0.5s ease-out;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_animated_header(title: str, subtitle: str):
    """Create an animated header with title and subtitle"""
    st.markdown(f"""
    <div class="animated-header">
        <h1>{title}</h1>
        <p class="animated-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def show_loading_animation(message: str):
    """Show a loading animation with custom message"""
    loading_placeholder = st.empty()
    
    loading_placeholder.markdown(f"""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">{message}...</div>
    </div>
    """, unsafe_allow_html=True)
    
    time.sleep(2)  # Simulate processing time
    loading_placeholder.empty()

def create_animated_card(content: str, card_type: str = "result"):
    """Create an animated card with content"""
    card_class = f"{card_type}-card"
    
    return f"""
    <div class="{card_class}">
        {content}
    </div>
    """

def show_progress_animation(steps: list, current_step: int):
    """Show animated progress for multi-step processes"""
    progress_html = "<div style='display: flex; justify-content: space-between; margin: 1rem 0;'>"
    
    for i, step in enumerate(steps):
        if i < current_step:
            # Completed step
            progress_html += f"""
            <div style='flex: 1; text-align: center; color: #00b894; font-weight: 600;'>
                ✅ {step}
            </div>
            """
        elif i == current_step:
            # Current step
            progress_html += f"""
            <div style='flex: 1; text-align: center; color: #667eea; font-weight: 600; animation: pulse 1s infinite;'>
                🔄 {step}
            </div>
            """
        else:
            # Future step
            progress_html += f"""
            <div style='flex: 1; text-align: center; color: #b2bec3; font-weight: 400;'>
                ⏳ {step}
            </div>
            """
    
    progress_html += "</div>"
    return progress_html

def create_floating_action_button(icon: str, text: str, key: str):
    """Create a floating action button with animation"""
    return st.button(
        f"{icon} {text}",
        key=key,
        help=f"Click to {text.lower()}",
        use_container_width=True
    )

def animate_text_reveal(text: str, delay: float = 0.1):
    """Create a text reveal animation effect"""
    words = text.split()
    animated_text = ""
    
    for i, word in enumerate(words):
        animated_text += f"""
        <span style='animation: fadeInUp 0.6s ease-out {i * delay}s both;'>{word} </span>
        """
    
    return f"<div>{animated_text}</div>"

def create_success_animation():
    """Create a success animation"""
    return """
    <div style='text-align: center; font-size: 4rem; animation: bounceIn 1s ease-out;'>
        🎉
    </div>
    """

def create_error_animation():
    """Create an error animation"""
    return """
    <div style='text-align: center; font-size: 3rem; animation: shake 0.5s ease-out;'>
        ❌
    </div>
    """
