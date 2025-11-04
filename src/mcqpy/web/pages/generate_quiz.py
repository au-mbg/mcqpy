"""
Quiz Generation Page

Generate quizzes from local or remote sources.
"""

import streamlit as st
import tempfile
from pathlib import Path
from typing import Dict, Optional
import yaml

from mcqpy.web.components.remote_quiz_loader import render_remote_quiz_loader, clear_remote_quiz


def show():
    """Render the quiz generation page"""
    
    st.title("🎯 Generate Quiz")
    st.markdown("Create quiz PDFs from local files or remote sources.")
    
    # Tabs for different input methods
    tab1, tab2 = st.tabs(["📁 Local Files", "🌐 Remote Source"])
    
    quiz_data = None
    
    with tab1:
        quiz_data = _render_local_file_input()
    
    with tab2:
        quiz_data = render_remote_quiz_loader()
        
        if st.button("🗑️ Clear Remote Quiz"):
            clear_remote_quiz()
            st.rerun()
    
    # Quiz generation section
    if quiz_data:
        st.markdown("---")
        _render_quiz_generation_section(quiz_data)


def _render_local_file_input() -> Optional[Dict]:
    """Render local file input section"""
    st.subheader("📁 Upload Local Quiz Files")
    st.markdown("Upload your config.yaml file and question YAML files.")
    
    uploaded_files = st.file_uploader(
        "Upload quiz files",
        type=['yaml', 'yml', 'json'],
        accept_multiple_files=True,
        help="Upload config.yaml and question YAML files"
    )
    
    if uploaded_files:
        return _process_local_files(uploaded_files)
    
    return None


def _process_local_files(uploaded_files) -> Optional[Dict]:
    """Process uploaded local files"""
    config_data = None
    questions = {}
    
    for file in uploaded_files:
        if file.name == 'config.yaml':
            config_data = yaml.safe_load(file.getvalue())
        elif file.name.endswith('.yaml') and 'question' in file.name:
            questions[file.name] = yaml.safe_load(file.getvalue())
    
    if config_data is None:
        st.warning("Please upload a config.yaml file")
        return None
    
    if not questions:
        st.warning("Please upload question YAML files")
        return None
    
    st.success(f"✅ Loaded {len(questions)} questions with configuration")
    
    return {
        'config': config_data,
        'questions': questions,
        'source_url': 'local_upload'
    }


def _render_quiz_generation_section(quiz_data: Dict):
    """Render the quiz generation controls and preview"""
    st.subheader("🎯 Generate Quiz")
    
    config = quiz_data['config']
    questions = quiz_data['questions']
    
    # Quiz options
    col1, col2 = st.columns(2)
    
    with col1:
        num_questions = st.number_input(
            "Number of questions",
            min_value=1,
            max_value=len(questions),
            value=min(10, len(questions)),
            help="How many questions to include in the quiz"
        )
    
    with col2:
        randomize = st.checkbox(
            "Randomize questions",
            value=True,
            help="Randomly select and order questions"
        )
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            quiz_title = st.text_input(
                "Quiz Title",
                value=config.get('file_name', 'Quiz'),
                help="Title for the generated quiz"
            )
        
        with col2:
            output_format = st.selectbox(
                "Output Format",
                ['PDF', 'LaTeX', 'Both'],
                help="Choose output format"
            )
    
    # Generate button
    if st.button("🚀 Generate Quiz", type="primary"):
        _generate_quiz(quiz_data, num_questions, randomize, quiz_title, output_format)


def _generate_quiz(quiz_data: Dict, num_questions: int, randomize: bool, 
                  quiz_title: str, output_format: str):
    """Generate the actual quiz"""
    
    with st.spinner("Generating quiz..."):
        try:
            # Create temporary directory for quiz generation
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Save config and questions to temporary files
                config_path = temp_path / "config.yaml"
                questions_dir = temp_path / "questions"
                questions_dir.mkdir()
                
                # Update config with user selections
                config = quiz_data['config'].copy()
                config['file_name'] = quiz_title
                
                # Save config
                with open(config_path, 'w') as f:
                    yaml.dump(config, f)
                
                # Save questions (limit to selected number if needed)
                question_items = list(quiz_data['questions'].items())
                if randomize:
                    import random
                    random.shuffle(question_items)
                
                selected_questions = question_items[:num_questions]
                
                for filename, question_data in selected_questions:
                    question_path = questions_dir / filename
                    with open(question_path, 'w') as f:
                        yaml.dump(question_data, f)
                
                # Create a simple build script using MCQPy CLI
                st.info("📝 Quiz files prepared. In a full implementation, this would call MCQPy's quiz generation functionality.")
                
                # Show what would be generated
                _show_generation_preview(config, selected_questions, temp_path)
                
        except Exception as e:
            st.error(f"❌ Error during quiz preparation: {str(e)}")


def _show_generation_preview(config: Dict, questions: list, temp_path: Path):
    """Show preview of what would be generated"""
    st.success("✅ Quiz files prepared successfully!")
    
    st.subheader("📋 Generation Preview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Questions Selected", len(questions))
    
    with col2:
        st.metric("Quiz Title", config.get('file_name', 'Quiz'))
    
    with col3:
        st.metric("Files Created", len(questions) + 1)  # +1 for config
    
    # Show selected questions
    with st.expander("📝 Selected Questions"):
        for i, (filename, question_data) in enumerate(questions, 1):
            question_text = question_data.get('question', 'No question text')
            st.write(f"**{i}. {filename}**: {question_text[:100]}...")
    
    # Show config
    with st.expander("⚙️ Configuration"):
        st.json(config)
    
    # In a real implementation, you would:
    st.info("""
    **Next Steps for Full Implementation:**
    
    1. Use MCQPy's CLI or create module to generate PDF
    2. Provide download buttons for generated files
    3. Generate manifest file for grading
    4. Add preview of generated quiz
    """)
    
    # Placeholder download buttons
    st.subheader("💾 Download Files")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("📄 Download PDF", disabled=True)
        st.caption("Would download generated PDF")
    
    with col2:
        st.button("📝 Download LaTeX", disabled=True)
        st.caption("Would download LaTeX source")
    
    with col3:
        st.button("📋 Download Manifest", disabled=True)
        st.caption("Would download quiz manifest")

if __name__ == "__main__":
    show()