from click.testing import CliRunner

from mcqpy.cli import export_web_command, main


def test_main_help_lists_export():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "export" in result.output


def test_export_web_cli(project_dir, mcqpy_project, written_questions):
    runner = CliRunner()
    output_dir = project_dir / "output" / "web-test"

    result = runner.invoke(
        export_web_command,
        ["-c", str(project_dir / "config.yaml"), "-o", str(output_dir)],
    )

    assert result.exit_code == 0
    assert (output_dir / "quiz.json").exists()
    assert (output_dir / "assets").exists()
