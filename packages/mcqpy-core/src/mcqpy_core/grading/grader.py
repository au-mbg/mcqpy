from pathlib import Path

from mcqpy_core.manifest import Manifest
from mcqpy_core.grading.types import GradedQuestion, GradedSet, ParsedSet
from mcqpy_core.grading.rubric import Rubric


def grade_parsed_set(manifest: Manifest, rubric: Rubric, parsed_set: ParsedSet) -> GradedSet:
    graded_set = GradedSet(student_info=parsed_set.student_info, graded_questions=[])

    for parsed_question in parsed_set.questions:
        manifest_item = manifest.get_item_by_qid(parsed_question.qid)

        graded_question = GradedQuestion(
            qid=parsed_question.qid,
            slug=parsed_question.slug,
            student_answers=parsed_question.onehot,
            correct_answers=manifest_item.correct_onehot,
            max_point_value=manifest_item.point_value,
        )

        if sum(graded_question.student_answers) == 0:
            raise Warning(
                f"No answers provided for question {graded_question.qid} ({graded_question.slug})"
            )

        graded_question.point_value = rubric.score_question(graded_question)
        graded_set.graded_questions.append(graded_question)

    graded_set.points = sum(q.point_value for q in graded_set.graded_questions)
    graded_set.max_points = sum(q.max_point_value for q in graded_set.graded_questions)
    return graded_set


class MCQGrader:
    def __init__(self, manifest: Manifest, rubric: Rubric, regex_pattern: str | None = None):
        self.manifest = manifest
        self.rubric = rubric
        self.regex_pattern = regex_pattern

    def grade(self, parsed_set: ParsedSet | None = None, student_answer: str | Path = None) -> GradedSet:
        if parsed_set is None:
            raise ValueError("MCQGrader.grade requires a ParsedSet in mcqpy-core")
        return grade_parsed_set(self.manifest, self.rubric, parsed_set)
