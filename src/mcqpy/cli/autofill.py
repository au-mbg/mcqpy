import contextlib
import io
from pathlib import Path

import numpy as np
import rich_click as click
from pypdf import PdfReader, PdfWriter
from rich.progress import track

from mcqpy.cli.config import QuizConfig
from mcqpy.cli.main import main
from mcqpy.build.manifest import Manifest


def get_student_name():
    first_names = [
        "Mikkel",
        "Sofie",
        "Frederik",
        "Emma",
        "William",
        "Ida",
        "Noah",
        "Anna",
        "Lucas",
        "Clara",
        "Oscar",
        "Laura",
        "Oliver",
        "Mathilde",
        "Alfred",
        "Katrine",
        "Emil",
    ]
    last_names = [
        "Jensen",
        "Nielsen",
        "Hansen",
        "Pedersen",
        "Andersen",
        "Christensen",
        "Larsen",
        "Sørensen",
        "Rasmussen",
        "Jørgensen",
        "Madsen",
        "Kristensen",
        "Olsen",
        "Johansen",
        "Poulsen",
        "Thomsen",
    ]

    return f"{np.random.choice(first_names)} {np.random.choice(last_names)}"


def fill_pdf_form(quiz_path, out_path, index=0, manifest=None):
    reader = PdfReader(quiz_path)
    writer = PdfWriter(fileobj=reader)

    # for page in reader.pages:
    #     writer.add_page(page)

    fields = reader.get_fields()
    keys = list(fields.keys())
    qid_name_dict = {}
    for key in keys:
        qid_idx = key.find("qid")
        if qid_idx != -1:
            qid = key[qid_idx + 4 :]

            if qid not in qid_name_dict:
                qid_name_dict[qid] = [key]
            else:
                qid_name_dict[qid].append(key)

    update_dict = {}
    for qid, names in qid_name_dict.items():
        if manifest:
            question = manifest.get_item_by_qid(qid)
            correct_choice = np.argwhere(question.correct_onehot).flatten()[0]
            if question is not None and correct_choice is not None:
                correct_prob = (1 / question.point_value) if question.point_value else 0.5
                other_prob = (1 - correct_prob) / (len(question.correct_onehot) - 1)
                probs = [other_prob] * len(question.correct_onehot)
                probs[correct_choice] = correct_prob
                name_to_fill = np.random.choice(
                    names, p=probs
                )
            else:
                name_to_fill = np.random.choice(names)

        update_dict[name_to_fill] = "/Yes"  # select answer A for all questions

    update_dict.update({"studentname": f"{get_student_name()}", "studentid": f"TID{index}"})

    writer.update_page_form_field_values(None, update_dict)

    with open(out_path / f"{quiz_path.stem}_autofill_{index}.pdf", "wb") as output_pdf:
        writer.write(output_pdf)


@main.command(
    name="test-autofill",
    help="Make answered versions of quiz to test mcqpy functionality",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default="config.yaml",
    help="Path to the config file",
    show_default=True,
)
@click.option(
    "-n",
    "--num-forms",
    type=int,
    default=10,
    help="Number of filled forms to generate",
    show_default=True,
)
def autofill_command(config, num_forms):
    # Directories & files
    config = QuizConfig.read_yaml(config)
    file_path = Path(config.output_directory) / config.file_name
    output_dir = Path(config.submission_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = Path(config.file_name).stem
    manifest_path = Path(config.output_directory) / f"{file_name}_manifest.json"
    manifest = Manifest.load_from_file(manifest_path)


    # In the autofill_command function
    for i in track(range(num_forms), description="Generating filled forms..."):
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with (
            contextlib.redirect_stdout(stdout_capture),
            contextlib.redirect_stderr(stderr_capture),
        ):
            fill_pdf_form(file_path, out_path=output_dir, index=i, manifest=manifest)

    click.echo(f"Generated {num_forms} filled forms based on {file_path}")
