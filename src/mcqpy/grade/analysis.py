import pandas as pd
from mcqpy.grade.utils import GradedSet, GradedQuestion
import numpy as np
from pathlib import Path

def get_grade_dataframe(graded_sets: list[GradedSet]) -> pd.DataFrame:

    records = []
    for graded_set in graded_sets:
        record = {
            "student_id": graded_set.student_id,
            "student_name": graded_set.student_name,
            "total_points": graded_set.points,
            "max_points": graded_set.max_points,  
            }

        for index, graded_question in enumerate(graded_set.graded_questions):
            record[f"Q{index+1}_points"] = graded_question.point_value
        
        records.append(record)

    df = pd.DataFrame.from_records(records)
    df.sort_values(by="student_name", inplace=True)
    return df

def question_analysis(graded_questions: list[GradedQuestion], out_directory: str | Path = None):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), layout='constrained')


    fig.suptitle(f"Question Analysis: {graded_questions[0].slug}")

    # Answer distribution: 
    all_onehots = np.vstack([q.student_answers for q in graded_questions])
    answer_sums = all_onehots.sum(axis=0)
    answer_labels = [f"{chr(i+65)}" for i in range(all_onehots.shape[1])]

    correct_answers = graded_questions[0].correct_answers

    colors = ['green' if correct_answers[i] == 1 else 'red' for i in range(len(correct_answers))]

    ax = axes[0]
    ax.bar(answer_labels, answer_sums, color=colors, alpha=0.7, edgecolor='black')
    ax.set_xlabel("Answer Options")
    ax.set_ylabel("Number of Selections")
    ax.set_title("Distribution of Selected Answers")


    # Score distribution:
    scores = [q.point_value for q in graded_questions]
    ax = axes[1]
    ax.hist(scores, bins=np.arange(-0.5, max(scores)+1.5, 1), color='blue', alpha=0.7, edgecolor='black')
    ax.set_xticks(np.arange(0, max(scores)+1, 1))
    ax.set_xlabel("Points Awarded")
    ax.set_ylabel("Number of Students")
    ax.set_title("Distribution of Points Awarded")

    plt.savefig(Path(out_directory) / f"question_analysis_{graded_questions[0].slug}.png") if out_directory else None
    plt.close(fig)


