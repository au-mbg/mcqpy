from mcqpy_core.grading.types import GradedSet

def get_grade_dataframe(
    graded_sets: list[GradedSet], sort_key: str | None = None
):
    try:
        import pandas as pd
    except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
        raise ModuleNotFoundError(
            "pandas is required for grade dataframe export. "
            "Install mcqpy-core with the 'grading' extra."
        ) from exc

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
