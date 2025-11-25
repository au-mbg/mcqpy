import os

def test_autofill_exit_code(autofill_invoke) -> None:
    assert autofill_invoke.exit_code == 0

def test_autofill_pdfs_exist(project_config) -> None:
    submission_dir = project_config.submission_directory
    files = os.listdir(submission_dir)
    pdf_files = [f for f in files if f.endswith(".pdf")]
    assert len(pdf_files) == 5