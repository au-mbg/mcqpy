
from pylatex import (
    Document,
    Enumerate,
    Figure,
    Section,
    SubFigure,
    Subsection
)
from pylatex.utils import NoEscape

from mcqpy.compile.latex_helpers import Form, code_block, multi_checkbox, radio_option
from mcqpy.question import Question
from mcqpy.utils.image import check_and_download_tmp


def build_question(document: Document, question: Question, quiz_index: int, add_solution: bool = False):
    if question.question_type == "single":
        extra_section_header = r"Select \underline{one} answer"
    elif question.question_type == "multiple":
        extra_section_header = r"Select \underline{all} correct answers"
    else:
        extra_section_header = ""

    with document.create(
        Section(
            NoEscape(
                rf"Question {quiz_index + 1} {{\small [{question.point_value} points]}} \hfill {{\small \textit{{{extra_section_header}}}}}"
            ),
            numbering=False,
        )
    ):
        document.append(NoEscape(question.text))

        _build_question_image(document, question)
        _build_question_code(document, question)
        _build_question_form(document, question, quiz_index, add_solution)
        if add_solution:
            _build_question_explanation(document, question)

def _build_question_explanation(document, question: Question):

    title = "Explanation and Correct Answer" if question.explanation else "Correct Answer"

    with document.create(Subsection(title, numbering=False)):

        permuted_correct_answers = [
            question.permutation.index(ans_idx) for ans_idx in question.correct_answers
        ]

        answer_string = ", ".join(
            [chr(97 + idx) for idx in permuted_correct_answers]
        )
        document.append(f"Correct answer(s): {answer_string}\n\n")

        if question.explanation:
            document.append(NoEscape(question.explanation))


def _build_question_code(document, question: Question):
    if not question.code:
        return

    for index, code_snippet in enumerate(question.code):
        if code_snippet is None:
            continue
        language = (
            question.code_language[index]
            if index < len(question.code_language)
            else "python"
        )
        document.append(code_block(code_snippet, language))


def _build_question_image(document, question: Question):
    if not question.image:
        return

    if len(question.image) == 1:
        image = question.image[0]
        image = check_and_download_tmp(image, f"tmp_question_{question.qid}_image_0")
        options = question.image_options.get(0, {}) if question.image_options else {}
        for key, value in options.items():
            options[key] = NoEscape(value)

        with document.create(Figure(position="h!")) as fig:
            fig.add_image(str(image), **options)
            if question.image_caption and 0 in question.image_caption:
                fig.add_caption(NoEscape(f"Figure: {question.image_caption[0]}"))
    else:
        with document.create(
            Figure(position="h!"),
        ) as fig:
            document.append(NoEscape(r"\centering"))
            for index, image in enumerate(question.image):
                options = (
                    question.image_options.get(index, {})
                    if question.image_options
                    else {}
                )

                image = check_and_download_tmp(
                    image, f"tmp_question_{question.qid}_image_{index}"
                )

                newline = options.pop(
                    "newline", None
                )  # Remove newline option if present
                if newline:
                    fig.append(NoEscape(r"\\"))

                for key, value in options.items():
                    options[key] = NoEscape(value)

                with document.create(SubFigure(position="b")) as subfig:
                    subfig.add_image(str(image), **options)
                    if question.image_caption and index in question.image_caption:
                        subfig.add_caption(NoEscape(f"{question.image_caption[index]}"))

            if question.image_caption and -1 in question.image_caption:
                fig.add_caption(NoEscape(f"Figure: {question.image_caption[-1]}"))


def _build_question_form(document, question: Question, quiz_index: int, add_solution: bool = False):
    with document.create(Form()):
        q_slug = question.slug
        q_qid = question.qid

        with document.create(Enumerate(enumeration_symbol=r"(\alph*)", options={})) as enum:
            for i, permute_index in enumerate(question.permutation):
                choice = question.choices[permute_index]

                if add_solution and permute_index in question.correct_answers:
                    checked = True
                else:
                    checked = False

                if question.question_type == "multiple":
                    command = multi_checkbox(
                        quiz_index=quiz_index,
                        q_slug=q_slug,
                        q_qid=q_qid,
                        i=i,
                        checked=checked,
                    )

                elif question.question_type == "single":
                    command = radio_option(
                        quiz_index=quiz_index,
                        q_slug=q_slug,
                        q_qid=q_qid,
                        i=i,
                        checked=checked,
                    )

                enum.add_item(command)
                enum.append(
                    NoEscape(
                        rf"\quad \begin{{minipage}}{{\textwidth}} {choice} \end{{minipage}}"
                    )
                )
