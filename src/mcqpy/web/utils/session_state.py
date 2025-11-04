"""
Session state management utilities for MCQPy web interface
"""

import streamlit as st
from typing import Any, Dict, List


class SessionStateManager:
    """Manage Streamlit session state with convenience methods"""
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Get value from session state with default"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """Set value in session state"""
        st.session_state[key] = value
    
    @staticmethod
    def delete(key: str) -> None:
        """Delete key from session state if it exists"""
        if key in st.session_state:
            del st.session_state[key]
    
    @staticmethod
    def clear_all() -> None:
        """Clear all session state"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    @staticmethod
    def initialize_defaults(defaults: Dict[str, Any]) -> None:
        """Initialize session state with default values if not already set"""
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def get_grading_results() -> List:
        """Get grading results from session state"""
        return SessionStateManager.get('grading_results', [])
    
    @staticmethod
    def set_grading_results(results: List) -> None:
        """Set grading results in session state"""
        SessionStateManager.set('grading_results', results)
    
    @staticmethod
    def clear_grading_results() -> None:
        """Clear grading results from session state"""
        SessionStateManager.delete('grading_results')
    
    @staticmethod
    def get_uploaded_manifest():
        """Get uploaded manifest from session state"""
        return SessionStateManager.get('uploaded_manifest', None)
    
    @staticmethod
    def set_uploaded_manifest(manifest) -> None:
        """Set uploaded manifest in session state"""
        SessionStateManager.set('uploaded_manifest', manifest)