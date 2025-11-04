"""
Configuration settings for MCQPy web interface
"""

import streamlit as st
from pathlib import Path



class WebConfig:
    """Configuration manager for the web interface"""
    
    def __init__(self):
        self.app_title = "MCQPy Web Interface"
        self.app_version = "0.1.0"
        self.max_file_size_mb = 10
        self.allowed_file_types = ['.pdf']
        
        # Initialize session state defaults
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state variables"""
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'manifest_file' not in st.session_state:
            st.session_state.manifest_file = None
        if 'grading_results' not in st.session_state:
            st.session_state.grading_results = []
    
    def clear_session(self):
        """Clear all session state"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        self._init_session_state()
    
    @property
    def max_file_size_bytes(self) -> int:
        """Maximum file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024