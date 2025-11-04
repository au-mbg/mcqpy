"""
MCQPy Streamlit Web Application

Main entry point for the MCQPy web interface.
Provides a multi-page app structure for extensibility.
"""

import streamlit as st
from mcqpy.web.config import WebConfig


def main():
    """Main Streamlit application entry point"""
    
    # Configure the page
    st.set_page_config(
        page_title="MCQPy Web Interface",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize configuration (for future use)
    # WebConfig()


    home_page = st.Page("pages/home.py", title="🏠 Home")
    grading_page = st.Page("pages/grade_pdf.py", title="📄 Grade PDF")
    generate_quiz_page = st.Page("pages/generate_quiz.py", title="🎯 Generate Quiz")
    question_form_page = st.Page("pages/question_form.py", title="❓ Question Form")
    test_page = st.Page("pages/test.py", title="🧪 Test")

    page_dict = {
        '': [home_page],
        'Tools': [grading_page, generate_quiz_page],
        'Forms': [question_form_page],
        'Testing': [test_page]
    }

    pg = st.navigation(page_dict)
    pg.run()

if __name__ == "__main__":
    main()