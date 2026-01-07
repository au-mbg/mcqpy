from click.testing import CliRunner
import os
import pytest

from mcqpy.cli import init_command, build_command, autofill_command, grade_command
from mcqpy.cli.config import QuizConfig

################################################################################
# Project initialization fixtures
################################################################################

@pytest.fixture(scope="session")
def project_dir(tmp_path_factory):
    path = tmp_path_factory.mktemp("mcqpy_project/")
    return path / "test_project"

@pytest.fixture(scope="session")
def mcqpy_project(project_dir):
    os.chdir(project_dir.parent)  # Change to the parent directory
    runner = CliRunner()
    result = runner.invoke(init_command, [str(project_dir.name)])
    return result

@pytest.fixture(scope="session")
def config_path(project_dir, mcqpy_project):
    return project_dir / "config.yaml"

@pytest.fixture(scope="session")
def project_config(config_path) -> QuizConfig:
    config = QuizConfig.read_yaml(config_path)
    return config

################################################################################
# Question fixtures
################################################################################

@pytest.fixture(scope="session")
def written_questions(project_dir, mcqpy_project, question_set):
    question_dir = project_dir / "questions"
    paths = []
    for question in question_set:
        yaml = question.as_yaml()
        path = question_dir / f"{question.qid}.yaml"
        paths.append(path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(yaml)
    return paths

################################################################################
# Built project fixtures
################################################################################

@pytest.fixture(scope="session")
def built_project(project_dir, mcqpy_project, written_questions):
    runner = CliRunner()
    os.chdir(project_dir)
    result = runner.invoke(build_command)
    return result

@pytest.fixture(scope="session")
def built_pdf_path(project_dir, project_config, built_project):
    output_dir = project_dir / project_config.output_directory
    pdf_path = output_dir / project_config.file_name
    return pdf_path

@pytest.fixture(scope="session")
def built_manifest_path(project_dir, project_config, built_project):
    output_dir = project_dir / project_config.output_directory
    manifest_path = output_dir / project_config.file_name.replace(".pdf", "_manifest.json")
    return manifest_path

################################################################################
# Autofill fixtures
################################################################################

@pytest.fixture(scope="session")
def autofill_invoke(built_project, project_dir):
    runner = CliRunner()
    os.chdir(project_dir)
    result = runner.invoke(autofill_command, ['-n', 5])
    return result

################################################################################
# Grade fixtures
################################################################################

@pytest.fixture(scope="session", params=['csv', 'xlsx'])
def grade_invoke(autofill_invoke, project_dir, request):
    runner = CliRunner()
    os.chdir(project_dir)
    result = runner.invoke(grade_command, ['-a', '-f', request.param])
    return result
    
