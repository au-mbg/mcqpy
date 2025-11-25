from pathlib import Path

from pylatex import (
    Command,
    Document,
    Foot,
    Head,
    PageStyle,
    LongTable,
    Section,
)
from pylatex.package import Package
from pylatex.utils import NoEscape


from mcqpy.build.latex_helpers import Form
from mcqpy.build.latex_questions import build_question
from mcqpy.build.manifest import Manifest, ManifestItem
from mcqpy.question import Question

from mcqpy.build.latex_questions import build_question


class SolutionPDF(Document):

    def __init__(
        self,
        manifest: Manifest,
        questions: list[Question],
        file: Path | str | None = None,
    ):
        super().__init__(
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
        self.file = Path(file) if file is not None else Path("default_solutions.pdf")
        self.manifest = manifest

        ## Sort questions by manifest

        manifest_qids = [item.qid for item in self.manifest.items]
        question_ids = [question.qid for question in questions]

        sorted_questions = []
        for qid in manifest_qids:
            if qid in question_ids:
                sorted_questions.append(
                    questions[question_ids.index(qid)]
                )
        self._questions = sorted_questions


    def build(self, generate_pdf: bool = False, **kwargs):        
        self.preamble.append(Package("caption"))
        self.preamble.append(Package("xcolor", options=["dvipsnames"]))
        self.preamble.append(Package("minted"))
        self.preamble.append(NoEscape(r"\usemintedstyle{vs}"))
        self.preamble.append(NoEscape(r"\captionsetup[figure]{labelformat=empty}"))

        self._build_solution_table()
        self._build_questions()
        if generate_pdf:
            default_kwargs = {"clean_tex": True}
            default_kwargs.update(kwargs)
            self.generate_pdf(self.file.with_suffix(""), **default_kwargs)

    def _build_solution_table(self) -> None:
        with self.create(Section("Solution Key", numbering=False)):
            with self.create(LongTable("l c")) as table:
                table.add_hline()
                table.add_row(("Question ID", "Correct Answer(s)"))
                table.add_hline()
                table.end_table_header()
                for index, question in enumerate(self._questions):
                    
                    answer_text = ""
                    for answer in question.correct_answers:
                        answer_text += f"({chr(97 + answer)}) "  #  Convert to a, b, c, d... 

                    table.add_row((index+1, answer_text))
                table.add_hline()
        
        self.append(NoEscape(r"\newpage"))

    def _build_questions(self):

        for index, question in enumerate(self._questions):
            build_question(self, question, index, add_solution=True)
            self.append(NoEscape(r"\newpage"))



