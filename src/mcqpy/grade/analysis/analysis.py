import re
from pathlib import Path

from pylatex import (
    Command,
    Document,
    Enumerate,
    Figure,
    LongTable,
    MultiColumn,
    NewPage,
    NoEscape,
    Package,
    Section,
)
from rich.console import Console
from rich.progress import track

from mcqpy.cli.config import GradingConfig
from mcqpy.compile.preamble import add_preamble
from mcqpy.grade.utils import GradedSet, get_grade_dataframe
from mcqpy.question import QuestionBank
from mcqpy.grade.analysis.question_analysis import question_analysis
from mcqpy.grade.analysis.overall_analysis import make_quiz_analysis


class QuizAnalysis(Document):
    def __init__(
        self,
        graded_sets: list[GradedSet],
        question_bank: QuestionBank,
        output_dir: str | Path = None,
        console: Console = None,
        grading_config: GradingConfig | None = None,
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
        self.graded_sets = graded_sets
        self.output_dir = Path(output_dir)
        self.figure_directory = self.output_dir / "figures"
        self.figure_directory.mkdir(parents=True, exist_ok=True)
        self.console = console or Console()
        self.question_bank = question_bank
        self.grading_config = grading_config or GradingConfig()

    def build(self):
        # Added TOC
        add_preamble(self)
        self.preamble.append(Package("xcolor", options=["dvipsnames"]))
        self.preamble.append(Command("title", "Quiz Analysis Report"))
        self.preamble.append(Command("author", "MCQPy"))
        self.preamble.append(Command("date", NoEscape(r"\today")))
        self.append(NoEscape(r"\maketitle"))
        self.append(NoEscape(r"\tableofcontents"))
        self.append(NewPage())

        self.console.log("Building quiz analysis...")
        self.build_quiz_analysis()
        self.console.log("Building question analysis...")
        self.build_question_analyses()
        self.console.log("Building grade table...")
        self.build_grade_table()

        self.console.log("Generating PDF...")
        self.generate_pdf(self.output_dir / "quiz_analysis", clean_tex=True)
        self.console.log("Finished generating PDF.")

    def build_quiz_analysis(self):
        figures = make_quiz_analysis(self.graded_sets, self.figure_directory)
        with self.create(Section("Overall Quiz Analysis", numbering="0")):
            for figure in figures:
                with self.create(Figure(position="h!")) as fig:
                    fig.add_image(
                        (Path("figures") / figure.name).as_posix(),
                        width=NoEscape(r"0.8\textwidth"),
                    )
                    fig.add_caption(NoEscape(figure.caption))

        self.append(NoEscape(r"\clearpage"))
        self.append(NewPage())

    def build_question_analyses(self):
        num_questions = len(self.graded_sets[0].graded_questions)
        for q_index in track(
            range(num_questions), description="Generating question analyses"
        ):
            with self.create(Section(f"Question {q_index + 1} Analysis")):
                graded_questions = [
                    gs.graded_questions[q_index] for gs in self.graded_sets
                ]

                figures = question_analysis(
                    graded_questions=graded_questions,
                    graded_sets=self.graded_sets,
                    out_directory=self.figure_directory,
                )

                question = self.question_bank.get_by_qid(graded_questions[0].qid)

                self.append(NoEscape(question.text))

                with self.create(
                    Enumerate(enumeration_symbol=r"(\alph*)", options={})
                ) as enum:
                    for choice in question.choices:
                        enum.add_item(NoEscape(choice))

                for figure in figures:
                    with self.create(Figure(position="h!")) as fig:
                        self.append(NoEscape(r"\centering"))
                        fig.add_image(
                            (Path("figures") / figure.name).as_posix(), width=NoEscape(r"0.8\textwidth")
                        )
                        fig.add_caption(
                            f"Analysis for Question {q_index + 1}: {figure.caption}"
                        )

                self.append(NewPage())

    def build_grade_table(self):
        df = get_grade_dataframe(
            self.graded_sets, sort_key=self.grading_config.output_sort_key
        )

        keys = []

        for key in df.keys().tolist():
            if re.match(r"Q\d+_points", key) or key in ["max_points"]:
                continue
            keys.append(key)

        with self.create(Section("Grade Summary Table")):
            with self.create(LongTable("l" * len(keys))) as data_table:
                data_table.add_hline()
                data_table.add_row(keys)
                data_table.add_hline()
                data_table.end_table_header()
                data_table.add_hline()
                data_table.add_row(
                    (MultiColumn(len(keys), align="r", data="Continued on Next Page"),)
                )
                data_table.add_hline()
                data_table.end_table_footer()
                data_table.add_hline()
                data_table.add_row(
                    (
                        MultiColumn(
                            len(keys), align="r", data="Not Continued on Next Page"
                        ),
                    )
                )
                data_table.add_hline()
                data_table.end_table_last_footer()

                for row in df.itertuples(index=False):
                    row_data = []
                    for key in keys:
                        row_data.append(getattr(row, key))
                    data_table.add_row(row_data)
