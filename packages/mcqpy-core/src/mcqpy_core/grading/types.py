from dataclasses import dataclass

import pandas as pd


@dataclass
class ParsedQuestion:
    qid: str
    slug: str
    answers: list[int]
    onehot: list[int]


@dataclass
class ParsedSet:
    student_info: dict[str, str]
    questions: list[ParsedQuestion]
    file: str | None = None


@dataclass
class GradedQuestion:
    qid: str
    slug: str
    student_answers: list[int]
    correct_answers: list[int]
    max_point_value: int
    point_value: int = 0


@dataclass
class GradedSet:
    student_info: dict[str, str]
    graded_questions: list[GradedQuestion]
    points: int = 0
    max_points: int = 0


def get_grade_dataframe(
    graded_sets: list[GradedSet], sort_key: str | None = None
) -> pd.DataFrame:
    records = []
    for graded_set in graded_sets:
        record = {}
        record.update(graded_set.student_info)
        record.update(
            {
                "total_points": graded_set.points,
                "max_points": graded_set.max_points,
            }
        )

        for index, graded_question in enumerate(graded_set.graded_questions):
            record[f"Q{index + 1}_points"] = graded_question.point_value

        records.append(record)

    df = pd.DataFrame.from_records(records)
    if sort_key:
        df.sort_values(by=sort_key, inplace=True)
    return df
