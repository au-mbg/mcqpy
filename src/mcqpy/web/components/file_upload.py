"""
File upload component for MCQPy web interface
"""

import streamlit as st
from typing import List, Optional


class FileUploadComponent:
    """Component for handling file uploads with validation"""
    
    def __init__(self, max_size_mb: int = 10):
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def upload_pdf_files(self, 
                        key: str = "pdf_upload",
                        multiple: bool = True,
                        label: str = "Upload PDF files") -> Optional[List]:
        """Upload PDF files with validation"""
        
        uploaded_files = st.file_uploader(
            label,
            type=['pdf'],
            accept_multiple_files=multiple,
            key=key,
            help=f"Maximum file size: {self.max_size_mb}MB per file"
        )
        
        if uploaded_files:
            if not multiple:
                uploaded_files = [uploaded_files]
            
            # Validate file sizes
            valid_files = []
            for file in uploaded_files:
                if file.size > self.max_size_bytes:
                    st.error(f"❌ File '{file.name}' is too large ({file.size / 1024 / 1024:.1f}MB). Maximum size is {self.max_size_mb}MB.")
                else:
                    valid_files.append(file)
            
            if valid_files:
                if multiple:
                    st.success(f"✅ {len(valid_files)} valid PDF file(s) uploaded.")
                else:
                    st.success(f"✅ PDF file '{valid_files[0].name}' uploaded successfully.")
                
                return valid_files if multiple else valid_files[0]
        
        return None
    
    def upload_json_file(self, 
                        key: str = "json_upload",
                        label: str = "Upload JSON file") -> Optional[object]:
        """Upload JSON file with validation"""
        
        uploaded_file = st.file_uploader(
            label,
            type=['json'],
            key=key,
            help="Upload a JSON manifest file"
        )
        
        if uploaded_file:
            if uploaded_file.size > self.max_size_bytes:
                st.error(f"❌ File '{uploaded_file.name}' is too large. Maximum size is {self.max_size_mb}MB.")
                return None
            
            try:
                # Validate JSON format
                import json
                json.load(uploaded_file)
                uploaded_file.seek(0)  # Reset file pointer
                st.success(f"✅ JSON file '{uploaded_file.name}' uploaded successfully.")
                return uploaded_file
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON file: {str(e)}")
                return None
        
        return None