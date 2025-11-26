"""
PDF grading page for MCQPy web interface
"""

from io import StringIO
import streamlit as st
import tempfile
import json
from pathlib import Path
from typing import List

from mcqpy.grade import MCQGrader
from mcqpy.compile.manifest import Manifest
from mcqpy.grade.rubric import StrictRubric
from mcqpy.web.components.grading_display import GradingDisplayComponent




def show():
    """Display the PDF grading page"""
    
    st.title("📄 Grade PDFs")
    st.markdown("Upload answer PDFs and a quiz manifest to get automatic grading results.")
    st.markdown("---")
    
    # Initialize display component
    display_component = GradingDisplayComponent()
    
    # Step 1: Upload manifest file
    st.subheader("Step 1: Upload Quiz Manifest")
    st.markdown("Upload the JSON manifest file that was generated when you created the quiz.")

    tab1, tab2, tab3 = st.tabs(["📁  Upload manifest", "🔗  Link to manifest", "🔑  Manifest token"])

    manifest_data = None
    with tab1:
        manifest_file = st.file_uploader(
            "Choose manifest file",
            key="manifest_upload",
        help="This file contains the answer key and question metadata."
        )
        if manifest_file is not None:
            manifest_data = manifest_file.getvalue()
    with tab2:
        manifest_url = st.text_input(
            "Manifest URL",
            placeholder="https://example.com/path/to/manifest.json",
            help="Enter the URL to the manifest JSON file."
        )
        if manifest_url:
            try:
                import requests
                response = requests.get(manifest_url)
                response.raise_for_status()
                manifest_data = response.text
            except Exception as e:
                st.error(f"❌ Error fetching manifest from URL: {str(e)}")
                manifest_data = None

    with tab3:
        manifest_token = st.text_input(
            "Manifest Token",
            placeholder="Enter manifest token",
            help="Enter the token that encodes the manifest URL."
        )
        if manifest_token:
            from mcqpy.web.utils.tokenizer import decode_token
            manifest_token
            decoded_url = decode_token(manifest_token)
            if decoded_url:
                try:
                    import requests
                    response = requests.get(decoded_url)
                    response.raise_for_status()
                    manifest_data = response.text
                except Exception as e:
                    st.error(f"❌ Error fetching manifest from decoded URL: {str(e)}")
                    manifest_data = None
            else:
                st.error("❌ Invalid manifest token.")
                manifest_data = None
    
    manifest = None
    if manifest_data is not None:
        try:
            manifest = Manifest.model_validate_json(manifest_data)
            st.success(f"✅ Manifest loaded successfully! Found {len(manifest.items)} questions.")
            
            # Display manifest info
            with st.expander("Manifest Details"):
                st.json({
                    "questions": len(manifest.items),
                    "first_few_questions": [
                        {"qid": item.qid, "slug": item.slug, "points": item.point_value}
                        for item in list(manifest.items)[:3]
                    ]
                })
                
        except Exception as e:
            st.error(f"❌ Error loading manifest: {str(e)}")
            manifest = None
    
    # Step 2: Upload student PDFs (only if manifest is loaded)
    if manifest is not None:
        st.markdown("---")
        st.subheader("Step 2: Upload Answer PDF(s)")
        st.markdown("Upload one or more PDF files containing student answers.")
        
        pdf_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            key="pdf_upload",
            help="Select multiple PDF files to grade them in batch."
        )
        
        if pdf_files:
            st.info(f"📁 {len(pdf_files)} PDF file(s) selected for grading.")
            
            # Grade button
            if st.button("🎯 Grade All PDFs", type="primary", use_container_width=True):
                grade_pdfs(pdf_files, manifest, display_component)
    
    else:
        st.info("👆 Please upload a manifest file first to proceed with PDF grading.")
    
    # # Display previous results if any exist in session state
    # if 'grading_results' in st.session_state and st.session_state.grading_results:
    #     st.markdown("---")
    #     st.subheader("📊 Previous Results")
    #     display_component.show_results(st.session_state.grading_results)


def grade_pdfs(pdf_files: List, manifest: Manifest, display_component):
    """Grade uploaded PDF files"""
    
    graded_sets = []
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        for i, pdf_file in enumerate(pdf_files):
            status_text.text(f"Grading {pdf_file.name}...")
            
            # Save PDF to temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_pdf:
                tmp_pdf.write(pdf_file.read())
                tmp_pdf_path = tmp_pdf.name
            
            try:
                # Grade the PDF
                grader = MCQGrader(manifest, StrictRubric())
                graded_set = grader.grade(tmp_pdf_path)
                graded_sets.append(graded_set)
                
            except Exception as e:
                st.error(f"❌ Error grading {pdf_file.name}: {str(e)}")
                continue
            finally:
                # Clean up temporary file
                Path(tmp_pdf_path).unlink(missing_ok=True)
            
            # Update progress
            progress_bar.progress((i + 1) / len(pdf_files))
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if graded_sets:
            st.success(f"✅ Successfully graded {len(graded_sets)} PDF(s)!")
            
            # Store results in session state
            st.session_state.grading_results = graded_sets
            
            # Display results
            display_component.show_results(graded_sets)
        else:
            st.error("❌ No PDFs were successfully graded.")
            
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Unexpected error during grading: {str(e)}")

if __name__ == "__main__":
    show()