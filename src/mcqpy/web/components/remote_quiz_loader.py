"""
Remote Quiz Loader Component

UI component for loading quiz configurations from remote sources.
"""

import streamlit as st
from typing import Dict, Optional
from mcqpy.web.utils.remote_loader import load_remote_quiz


def render_remote_quiz_loader() -> Optional[Dict]:
    """
    Render remote quiz loader interface
    
    Returns:
        Quiz data dictionary if successfully loaded, None otherwise
    """
    st.subheader("📡 Load Quiz from Remote Source")
    
    # URL input
    url_help = """
    **Supported formats:**
    - GitHub directory: `https://github.com/user/repo/tree/main/quiz_folder`
    - Zip archive: `https://github.com/user/repo/archive/refs/heads/main.zip`
    - Direct zip file: `https://example.com/quiz.zip`
    """
    
    quiz_url = st.text_input(
        "Quiz URL",
        placeholder="https://github.com/user/repo/tree/main/test_quiz",
        help=url_help
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        load_button = st.button("🔄 Load Quiz", type="primary")
    
    with col2:
        if quiz_url and load_button:
            with st.spinner("Loading quiz from remote source..."):
                quiz_data = load_remote_quiz(quiz_url)
                
                if quiz_data:
                    st.success("✅ Quiz loaded successfully!")
                    
                    # Store in session state
                    st.session_state.remote_quiz_data = quiz_data
                    st.session_state.remote_quiz_url = quiz_url
                    
                    return quiz_data
                else:
                    st.error("❌ Failed to load quiz from URL")
                    return None
    
    # Show loaded quiz info if available
    if hasattr(st.session_state, 'remote_quiz_data'):
        _display_quiz_info(st.session_state.remote_quiz_data)
        return st.session_state.remote_quiz_data
    
    return None


def _display_quiz_info(quiz_data: Dict) -> None:
    """Display information about the loaded quiz"""
    st.markdown("---")
    st.subheader("📋 Loaded Quiz Information")
    
    config = quiz_data.get('config', {})
    questions = quiz_data.get('questions', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Questions", len(questions))
    
    with col2:
        quiz_title = config.get('title', config.get('file_name', 'Untitled Quiz'))
        st.metric("Quiz Title", quiz_title)
    
    with col3:
        st.metric("Source", "Remote")
    
    # Show config details
    with st.expander("📝 Quiz Configuration"):
        st.json(config)
    
    # Show questions list
    with st.expander("❓ Questions Overview"):
        for filename, question_data in questions.items():
            question_text = question_data.get('question', 'No question text')
            st.write(f"**{filename}**: {question_text[:100]}...")


def clear_remote_quiz() -> None:
    """Clear loaded remote quiz from session state"""
    if hasattr(st.session_state, 'remote_quiz_data'):
        del st.session_state.remote_quiz_data
    if hasattr(st.session_state, 'remote_quiz_url'):
        del st.session_state.remote_quiz_url