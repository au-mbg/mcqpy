from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from mcqpy.grade.utils import GradedQuestion, GradedSet
from mcqpy.grade.analysis.utils import AnalysisFigure
from mcqpy.grade.analysis.overall_analysis import get_points_array


def question_analysis(
    graded_questions: list[GradedQuestion],
    graded_sets: list[GradedSet],
    out_directory: str | Path = None,
) -> list[AnalysisFigure]:

    figures = []
    figures.append(
        combined_figure(
            graded_questions=graded_questions, graded_sets=graded_sets, out_directory=out_directory
        )
    )
    return figures

def answer_distribution_plot(ax, graded_questions: list[GradedQuestion]) -> None:
    # Answer distribution:
    all_onehots = np.vstack([q.student_answers for q in graded_questions])
    answer_sums = all_onehots.sum(axis=0)
    answer_labels = [f"{chr(i + 65)}" for i in range(all_onehots.shape[1])]

    correct_answers = graded_questions[0].correct_answers

    colors = [
        "green" if correct_answers[i] == 1 else "red"
        for i in range(len(correct_answers))
    ]

    ax.bar(answer_labels, answer_sums, color=colors, alpha=0.7, edgecolor="black")
    ax.set_xlabel("Answer Options")
    ax.set_ylabel("Number of Selections")
    ax.set_title("Distribution of Selected Answers")

def point_distribution_plot(ax, graded_questions: list[GradedQuestion]) -> None:
    # Score distribution:
    scores = [q.point_value for q in graded_questions]
    ax.hist(
        scores,
        bins=np.arange(-0.5, max(scores) + 1.5, 1),
        color="blue",
        alpha=0.7,
        edgecolor="black",
    )
    ax.set_xticks(np.arange(0, max(scores) + 1, 1))
    ax.set_xlabel("Points Awarded")
    ax.set_ylabel("Number of Students")
    ax.set_title("Distribution of Points Awarded")

def discriminator_plot(ax, graded_questions: list[GradedQuestion], graded_sets: list[GradedSet]) -> None:
    point_array = get_points_array(graded_sets)
    total_points_array = point_array.sum(axis=1)
    qidx = graded_sets[0].graded_questions.index(graded_questions[0])
    q_points = point_array[:, qidx]
    high_group = total_points_array >= np.percentile(total_points_array, 75)
    low_group = total_points_array <= np.percentile(total_points_array, 25)
    middle_group = (total_points_array > np.percentile(total_points_array, 25)) & (total_points_array < np.percentile(total_points_array, 75))
    ax.bar(["Top 25%", "25-75%", "Bottom 25%"], [np.mean(q_points[high_group]), np.mean(q_points[middle_group]), np.mean(q_points[low_group])], color=["green", "yellow", "red"], alpha=0.7, edgecolor="black")
    ax.set_ylabel("Average Points on Question")
    ax.set_title("Discriminator Analysis")


def combined_figure(
    graded_questions: list[GradedQuestion], graded_sets: list[GradedSet], out_directory: str | Path = None
) -> AnalysisFigure:
    fig, axes = plt.subplots(1, 3, figsize=(10, 5), layout="constrained")

    fig.suptitle(f"Question Analysis: {graded_questions[0].slug}")

    answer_distribution_plot(axes[0], graded_questions)
    point_distribution_plot(axes[1], graded_questions)
    discriminator_plot(axes[2], graded_questions, graded_sets)

    # Save figure
    name = f"{graded_questions[0].slug}.pdf"
    output_path = Path(out_directory) / name

    plt.savefig(output_path) if out_directory else None
    plt.close(fig)

    return AnalysisFigure(name=name, caption="""Left: Distribution of selected answers, with correct answers highlighted in green. Middle: Distribution of points awarded for the question. Right: Discriminator analysis showing average points on the question for top 25%, middle 50%, and bottom 25% of students based on total score.""")
