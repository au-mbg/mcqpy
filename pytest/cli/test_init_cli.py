
def test_init_exit_code(mcqpy_project) -> None:
    assert mcqpy_project.exit_code == 0

def test_init_project_directory_created(project_dir) -> None:
    assert project_dir.exists()

def test_init_config_file_created(project_dir) -> None:
    config_file = project_dir / "config.yaml"
    assert config_file.exists()

def test_init_questions_directory_created(project_dir) -> None:
    questions_dir = project_dir / "questions"
    assert questions_dir.exists()