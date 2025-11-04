"""
Input validation utilities for MCQPy web interface
"""

import json
from typing import Optional, Tuple, List


class FileValidator:
    """Validate uploaded files"""
    
    @staticmethod
    def validate_pdf_file(file_content: bytes, filename: str, max_size_mb: int = 10) -> Tuple[bool, str]:
        """
        Validate PDF file
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # Check file size
        if len(file_content) > max_size_bytes:
            return False, f"File size ({len(file_content) / 1024 / 1024:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
        
        # Check file extension
        if not filename.lower().endswith('.pdf'):
            return False, "File must have .pdf extension"
        
        # Basic PDF header check
        if not file_content.startswith(b'%PDF'):
            return False, "File does not appear to be a valid PDF"
        
        return True, ""
    
    @staticmethod
    def validate_json_file(file_content: bytes, filename: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Validate JSON file
        
        Returns:
            Tuple[bool, str, Optional[dict]]: (is_valid, error_message, parsed_data)
        """
        # Check file extension
        if not filename.lower().endswith('.json'):
            return False, "File must have .json extension", None
        
        # Try to parse JSON
        try:
            content_str = file_content.decode('utf-8')
            parsed_data = json.loads(content_str)
            return True, "", parsed_data
        except UnicodeDecodeError:
            return False, "File contains invalid UTF-8 characters", None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}", None
    
    @staticmethod
    def validate_manifest_structure(manifest_data: dict) -> Tuple[bool, str]:
        """
        Validate manifest file structure
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        required_fields = ['items']
        
        # Check required top-level fields
        for field in required_fields:
            if field not in manifest_data:
                return False, f"Missing required field: {field}"
        
        # Check items structure
        items = manifest_data.get('items', [])
        if not isinstance(items, list):
            return False, "Field 'items' must be a list"
        
        if len(items) == 0:
            return False, "Manifest must contain at least one question item"
        
        # Validate individual items
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                return False, f"Item {i} must be a dictionary"
            
            required_item_fields = ['qid', 'slug', 'correct_onehot', 'point_value']
            for field in required_item_fields:
                if field not in item:
                    return False, f"Item {i} missing required field: {field}"
        
        return True, ""


class FormValidator:
    """Validate form inputs"""
    
    @staticmethod
    def validate_student_id(student_id: str) -> Tuple[bool, str]:
        """Validate student ID format"""
        if not student_id or not student_id.strip():
            return False, "Student ID cannot be empty"
        
        if len(student_id.strip()) < 2:
            return False, "Student ID must be at least 2 characters long"
        
        return True, ""
    
    @staticmethod
    def validate_student_name(student_name: str) -> Tuple[bool, str]:
        """Validate student name format"""
        if not student_name or not student_name.strip():
            return False, "Student name cannot be empty"
        
        if len(student_name.strip()) < 2:
            return False, "Student name must be at least 2 characters long"
        
        return True, ""
    
    @staticmethod
    def validate_file_list(files: List, min_files: int = 1, max_files: int = 100) -> Tuple[bool, str]:
        """Validate list of uploaded files"""
        if not files:
            return False, f"Please upload at least {min_files} file(s)"
        
        if len(files) < min_files:
            return False, f"Please upload at least {min_files} file(s)"
        
        if len(files) > max_files:
            return False, f"Cannot upload more than {max_files} files at once"
        
        return True, ""