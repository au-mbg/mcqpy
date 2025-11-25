from pathlib import Path

def test_grade_exit_code(grade_invoke) -> None:
    assert grade_invoke.exit_code == 0

def test_grade_file_exists(grade_invoke, project_dir, project_config) -> None:
    file_name = Path(project_config.file_name).stem
    grade_file_xlsx = project_dir / f"{file_name}_grades.xlsx"
    grade_file_csv = project_dir / f"{file_name}_grades.csv"
    assert grade_file_xlsx.exists() or grade_file_csv.exists()

def test_analysis_directory_exists(grade_invoke, project_dir) -> None:
    analysis_dir = project_dir / "analysis"
    assert analysis_dir.exists()