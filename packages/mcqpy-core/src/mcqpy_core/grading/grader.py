from pathlib import Path

from mcqpy_core.manifest import Manifest
from mcqpy_core.grading.types import GradedQuestion, GradedSet, ParsedSet, GradeResult, GradeState
from mcqpy_core.grading.rubric import Rubric


def grade_parsed_set(manifest: Manifest, rubric: Rubric, parsed_set: ParsedSet) -> GradeResult:
    graded_set = GradedSet(student_info=parsed_set.student_info, graded_questions=[])

    other_info = {}
    for parsed_question in parsed_set.questions:
        manifest_item = manifest.get_item_by_qid(parsed_question.qid)

        graded_question = GradedQuestion(
            qid=parsed_question.qid,
            slug=parsed_question.slug,
            student_answers=parsed_question.onehot,
            correct_answers=manifest_item.correct_onehot,
            max_point_value=manifest_item.point_value,
        )

        if sum(parsed_question.onehot) == 0:
            message = f"No answers provided for question {parsed_question.qid} ({parsed_question.slug})."
            other_info[parsed_question.qid] = message

        graded_question.point_value = rubric.score_question(graded_question)
        graded_set.graded_questions.append(graded_question)

    graded_set.points = sum(q.point_value for q in graded_set.graded_questions)
    graded_set.max_points = sum(q.max_point_value for q in graded_set.graded_questions)
    return GradeResult(
        state=GradeState.SUCCESS,
        graded_set=graded_set,
        other_info=other_info if other_info else None,
    )


class MCQGrader:
    def __init__(self, manifest: Manifest, rubric: Rubric, regex_pattern: str | None = None):
        self.manifest = manifest
        self.rubric = rubric
        self.regex_pattern = regex_pattern

    def grade(self, parsed_set: ParsedSet | None = None, student_answer: str | Path = None) -> GradeResult:
        if parsed_set is None:
            raise ValueError("MCQGrader.grade requires a ParsedSet in mcqpy-core")
        return grade_parsed_set(self.manifest, self.rubric, parsed_set)
