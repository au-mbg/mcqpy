"""
Home page for MCQPy web interface
"""

import streamlit as st


def show():
    """Display the home page"""
    
    st.title("🎓 MCQPy Web Interface")
    st.markdown("---")
    
    st.markdown("""
    Welcome to the MCQPy web interface! This application provides a user-friendly 
    way to interact with MCQPy's multiple-choice quiz functionality.
    """)
    
    # Feature overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Current Features")
        st.markdown("""
        - **PDF Grading**: Upload student answer PDFs for automatic grading
        - **Results Analysis**: View detailed grading results and statistics
        - **Batch Processing**: Grade multiple submissions at once
        """)
    
    with col2:
        st.subheader("🚀 Coming Soon")
        st.markdown("""
        - **Interactive Quizzes**: Host live quiz sessions
        - **Question Builder**: Create and edit questions with preview
        - **Advanced Analytics**: Detailed performance insights
        """)
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🎯 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Grade PDFs", use_container_width=True):
            st.switch_page("pages/Grade_PDF.py")
    
    with col2:
        st.button("🎯 Interactive Quiz", disabled=True, use_container_width=True)
        st.caption("Coming soon!")
    
    with col3:
        st.button("❓ Question Builder", disabled=True, use_container_width=True)
        st.caption("Coming soon!")
    
    # Getting started
    st.markdown("---")
    st.subheader("🔧 Getting Started")
    
    with st.expander("How to grade PDFs"):
        st.markdown("""
        1. **Prepare your files**:
           - Student answer PDFs (from MCQPy-generated forms)
           - Quiz manifest JSON file (generated when creating the quiz)
        
        2. **Upload files**:
           - Go to the "Grade PDF" page
           - Upload your manifest file first
           - Upload one or more student answer PDFs
        
        3. **Review results**:
           - View individual student scores
           - Download results as Excel or CSV
           - Analyze question performance
        """)
    
    with st.expander("About MCQPy"):
        st.markdown("""
        MCQPy is a comprehensive tool for creating and grading multiple-choice quizzes.
        It generates professional PDF forms with automatic grading capabilities,
        making it ideal for educational institutions and training organizations.
        """)
    
    # Status information
    st.markdown("---")
    st.info("💡 **Tip**: Use the sidebar to navigate between different features.")

if __name__ == "__main__":
    show()