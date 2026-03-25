from mcqpy.cli import main


def test_umbrella_cli_registration():
    assert {"build", "grade", "export", "init", "question", "utils"} <= set(main.commands)
