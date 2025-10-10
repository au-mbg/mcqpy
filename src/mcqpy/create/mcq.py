from annotated_types import doc
from pylatex import (
    Document,
    Enumerate,
    Section,
    Command,
    Figure,
    SubFigure,
    PageStyle,
    Head,
    Foot,
    simple_page_number,
)
from pylatex.base_classes import Environment
from pylatex.package import Package
from pylatex.utils import NoEscape

from mcqpy.question import Question
from pathlib import Path
from dataclasses import dataclass, field

from mcqpy.create.manifest import Manifest, ManifestItem


class Form(Environment):
    """Form environment from hyperref."""

    _latex_name = "Form"

    packages = [Package("hyperref")]
    escape = False
    content_separator = " "


def radio_option(quiz_index: int, q_slug: str, q_qid: str, i: int) -> NoEscape:
    # One field name for the whole question; value carries which option is selected
    # return NoEscape(
    #     r"\raisebox{0pt}[0pt][0pt]{"
    #     + r"\CheckBox[radio,"
    #     + rf"name=Q{quiz_index}-slug={q_slug}-qid={q_qid},"
    #     + rf"value={i},"
    #     r"width=5mm,height=5mm,borderwidth=0.5,"
    #     r"bordercolor=0 0 0,backgroundcolor=1 1 1,color=0 0 0,"
    #     r"radiosymbol=circle"  # or: star, cross, square, diamond
    #     + rf"]{{{i}}}"
    #     + "}"
    # )
    return multi_checkbox(
        quiz_index=quiz_index,
        q_slug=q_slug,
        q_qid=q_qid,
        i=i,
    )


def multi_checkbox(quiz_index: int, q_slug: str, q_qid: str, i: int) -> NoEscape:
    command = NoEscape(
        r"\raisebox{0pt}[0pt][0pt]{\CheckBox"
        + f"[name=Q{quiz_index}-opt={i}-slug={q_slug}-qid={q_qid},"
        + r"width=1em,"
        + r"height=1em,"
        + r"bordercolor=0 0 0,"
        + r"backgroundcolor=1 1 1"
        + r"]{{}}"
        + "}"
    )
    return command


@dataclass
class FrontMatterOptions:
    title: str | None = None
    author: str | None = None
    date: str | None | bool = None
    exam_information: str | None = None


@dataclass
class HeaderFooterOptions:
    header_left: str | None = None
    header_center: str | None = None
    header_right: str | None = field(default=r"Page \thepage \ of \ \pageref{LastPage}")
    footer_left: str | None = None
    footer_center: str | None = None
    footer_right: str | None = None

class MultipleChoiceQuiz:
    def __init__(
        self,
        document: Document | None,
        file: Path | str | None = None,
        questions: list[Question] | None = None,
        front_matter: FrontMatterOptions | None = None,
        header_footer: HeaderFooterOptions | None = None,
    ):
        if document is None:
            document = Document(
                documentclass="article",
                geometry_options={
                    "paper": "a4paper",
                    "includeheadfoot": True,
                    "left": "2cm",
                    "right": "3cm",
                    "top": "2.5cm",
                    "bottom": "2.5cm",
                },
            )
        self.document = document
        self._questions = questions or []
        self.front_matter = front_matter or FrontMatterOptions()
        self.header_footer = header_footer or HeaderFooterOptions()
         # Default to page number on the right if nothing specified
        self.file = Path(file) if file is not None else Path("default_quiz")

    def get_questions(self) -> list[Question]:
        return self._questions

    ############################################################################
    # Build the document
    ############################################################################

    def build(self, generate_pdf: bool = False, **kwargs):
        doc = self.document
        doc.preamble.append(Package("caption"))
        doc.preamble.append(NoEscape(r"\captionsetup[figure]{labelformat=empty}"))

        # Front matter
        self._build_front_matter()
        self._build_header()

        # Questions:
        questions = self.get_questions()
        manifest_items = self._build_questions(questions)

        if generate_pdf:
            default_kwargs = {"clean_tex": True}
            default_kwargs.update(kwargs)
            self.document.generate_pdf(self.file, **default_kwargs)
            self._build_manifest(manifest_items)

    def _build_header(self):
        # Check if any header/footer option is not None
        if not any(value is not None for value in self.header_footer.__dict__.values()):
            print('No header or footer specified, skipping header/footer build.')
            return  # No header/footer to build

        print('Building header and footer...')
        header = PageStyle("header")

        for position, content in [
            ("L", self.header_footer.header_left),
            ("C", self.header_footer.header_center),
            ("R", self.header_footer.header_right),
        ]:  
            if content is not None:
                print(f'Adding header {position} with content: {content}')
                with header.create(Head(position)):
                    header.append(NoEscape(content))

        self.document.preamble.append(header)
        self.document.change_document_style("header")
            
    def _build_metadata(self):
        pass

    def _build_manifest(self, manifest_items: list[ManifestItem]):
        manifest = Manifest(items=manifest_items)
        manifest_path = self.file.with_name(self.file.name + "_manifest").with_suffix(
            ".json"
        )
        manifest.save_to_file(manifest_path)

    def _build_front_matter(self):
        doc = self.document
        if self.front_matter.title is not None:
            doc.preamble.append(Command("title", self.front_matter.title))

        if self.front_matter.author is not None:
            doc.preamble.append(Command("author", self.front_matter.author))

        if self.front_matter.date is not None:
            if isinstance(self.front_matter.date, str):
                doc.preamble.append(Command("date", self.front_matter.date))
            elif self.front_matter.date is True:
                doc.preamble.append(Command("date", NoEscape(r"\today")))

        doc.append(NoEscape(r"\maketitle"))
        self._build_id_fields()

        if self.front_matter.exam_information is not None:
            with doc.create(Section("Exam Information", numbering=False)):
                doc.append(NoEscape(self.front_matter.exam_information))

    def _build_id_fields(self):
        doc = self.document
        field_options = "width=0.7\\textwidth, bordercolor=0 0 0, backgroundcolor=1 1 1"
        with doc.create(Section("Student Information", numbering=False)):
            doc.append(
                NoEscape(
                    r"Please fill in your name and student ID below, this is \underline{important}! \\"
                )
            )
            # A little vspace
            doc.append(NoEscape(r"\\[5pt]"))
            with doc.create(Form()):
                raw_field = NoEscape(
                    r"\TextField[name=student_name, "
                    + field_options
                    + r"]{\textbf{Name}:}"
                )
                doc.append(raw_field)
                doc.append(NoEscape(r"\\[10pt]"))  # add some vertical space
                raw_field = NoEscape(
                    r"\TextField[name=student_id, " + field_options + r"]{\textbf{ID}:}"
                )
                doc.append(raw_field)

    def _build_questions(self, questions: list[Question]):
        manifest_items = []
        for quiz_index, question in enumerate(questions):
            self._build_question(question, quiz_index)
            manifest_items.append(
                ManifestItem.from_question(question, permutation=question.permutation)
            )

        return manifest_items

    def _build_question(self, question: Question, quiz_index: int):
        doc = self.document
        doc.append(Command("pagebreak"))

        if question.question_type == "single":
            extra_section_header = r"Select \underline{one} answer"
        elif question.question_type == "multiple":
            extra_section_header = r"Select \underline{all} correct answers"
        else:
            extra_section_header = ""

        with doc.create(
            Section(
                NoEscape(
                    rf"Question {quiz_index + 1} \hfill {{\small \textit{{{extra_section_header}}}}}"
                ),
                numbering=False,
            )
        ):
            doc.append(NoEscape(question.text))
            doc.append(NoEscape(r"\\[10pt]"))  # add some vertical space

            self._build_question_image(question)
            self._build_question_form(question, quiz_index)

    def _build_question_image(self, question: Question):
        doc = self.document
        if not question.image:
            return

        if len(question.image) == 1:
            image = question.image[0]
            options = (
                question.image_options.get(0, {}) if question.image_options else {}
            )
            for key, value in options.items():
                options[key] = NoEscape(value)

            with doc.create(Figure(position="h!")) as fig:
                fig.add_image(str(image), **options)
                if question.image_caption and 0 in question.image_caption:
                    fig.add_caption(NoEscape(f"Figure: {question.image_caption[0]}"))
        else:
            with doc.create(
                Figure(position="h!"),
            ) as fig:
                doc.append(NoEscape(r"\centering"))
                for index, image in enumerate(question.image):
                    options = (
                        question.image_options.get(index, {})
                        if question.image_options
                        else {}
                    )

                    newline = options.pop(
                        "newline", None
                    )  # Remove newline option if present
                    if newline:
                        fig.append(NoEscape(r"\\"))

                    for key, value in options.items():
                        options[key] = NoEscape(value)

                    with doc.create(SubFigure(position="b")) as subfig:
                        subfig.add_image(str(image), **options)
                        if question.image_caption and index in question.image_caption:
                            subfig.add_caption(
                                NoEscape(f"{question.image_caption[index]}")
                            )

                if question.image_caption and -1 in question.image_caption:
                    fig.add_caption(NoEscape(f"Figure: {question.image_caption[-1]}"))

    def _build_question_form(self, question: Question, quiz_index: int):
        doc = self.document
        with doc.create(Form()):
            q_slug = question.slug
            q_qid = question.qid

            with doc.create(
                Enumerate(enumeration_symbol=r"(\alph*)", options={})
            ) as enum:
                for i, permute_index in enumerate(question.permutation):
                    choice = question.choices[permute_index]

                    if question.question_type == "multiple":
                        command = multi_checkbox(
                            quiz_index=quiz_index,
                            q_slug=q_slug,
                            q_qid=q_qid,
                            i=i,
                        )

                    elif question.question_type == "single":
                        command = radio_option(
                            quiz_index=quiz_index,
                            q_slug=q_slug,
                            q_qid=q_qid,
                            i=i,
                        )

                    enum.add_item(command)
                    enum.append(
                        NoEscape(
                            rf"\quad \begin{{minipage}}{{\textwidth}} {choice} \end{{minipage}}"
                        )
                    )
