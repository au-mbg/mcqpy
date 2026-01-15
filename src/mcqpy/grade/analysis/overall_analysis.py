from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np

from mcqpy.grade.utils import GradedSet
from scipy.stats import pearsonr

from dataclasses import dataclass


@dataclass
class AnalysisFigure:
    name: str
    caption: str


def get_points_array(graded_sets: list[GradedSet]):
    point_arrays = np.zeros((len(graded_sets), 20))
    for i, graded_set in enumerate(graded_sets):
        for j, question in enumerate(graded_set.graded_questions):
            point_arrays[i, j] = question.point_value
    return point_arrays


def correlation_analysis(graded_sets: list[GradedSet], output_dir: str | Path):
    point_array = get_points_array(graded_sets)
    total_points_array = point_array.sum(axis=1)

    n_questions = point_array.shape[1]

    correlations = np.zeros(n_questions)
    p_values = np.zeros(n_questions)

    for qidx in range(n_questions):
        q_points = point_array[:, qidx]
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            correlation, p_value = pearsonr(q_points, (total_points_array - q_points))

        correlations[qidx] = correlation
        p_values[qidx] = p_value

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        np.arange(1, n_questions + 1),
        correlations,
        color="mediumpurple",
        alpha=0.7,
        edgecolor="black",
    )
    plt.xlabel("Question Number")
    plt.ylabel("Correlation")
    plt.title("Correlation Analysis of Questions")

    ax.set_xticks(np.arange(1, n_questions + 1))

    plt.tight_layout()

    name = "quiz_correlation_analysis.pdf"
    output_path = output_dir / name

    plt.savefig(output_path)
    plt.close()
    return AnalysisFigure(
        name=name,
        caption=r"\textbf{Correlation Analysis}: Measures how well performance on each question correlates with overall quiz performance.",
    )


def point_distribution_analysis(graded_sets: list[GradedSet], output_dir: str | Path):
    point_distribution = np.array([gs.points for gs in graded_sets])
    max_points = graded_sets[0].max_points

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(
        point_distribution,
        bins=np.arange(-0.5, max_points + 1.5, 1),
        facecolor="mediumpurple",
        alpha=0.7,
        edgecolor="black",
    )

    ax.axvline(max_points, color="red", linestyle="dashed", linewidth=1)

    ax.set_xlabel("Total Points")
    ax.set_ylabel("Number of Students")
    ax.set_title("Distribution of Total Points")

    name = "quiz_point_distribution_analysis.pdf"
    output_path = output_dir / name

    plt.savefig(output_path)
    plt.close()
    return AnalysisFigure(
        name=name,
        caption=r"\textbf{Total points distribution}: Shows how total points are distributed among students, with a red dashed line indicating the maximum possible points.",
    )


def discrimination_index_analysis(graded_sets: list[GradedSet], output_dir: str | Path):
    point_array = get_points_array(graded_sets)
    total_points_array = point_array.sum(axis=1)

    n_questions = point_array.shape[1]

    discrimination_indices = np.zeros(n_questions)

    for qidx in range(n_questions):
        q_points = point_array[:, qidx]
        max_score = graded_sets[0].graded_questions[qidx].max_point_value
        high_group = total_points_array >= np.percentile(total_points_array, 75)
        low_group = total_points_array <= np.percentile(total_points_array, 25)

        D = (np.mean(q_points[high_group]) - np.mean(q_points[low_group])) / max_score
        discrimination_indices[qidx] = D

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(
        np.arange(1, n_questions + 1),
        discrimination_indices,
        color="mediumpurple",
        alpha=0.7,
        edgecolor="black",
    )
    plt.xlabel("Question Number")
    plt.ylabel("Discrimination Index")
    plt.title("Discrimination Index Analysis of Questions")

    ax.set_xticks(np.arange(1, n_questions + 1))

    plt.tight_layout()

    name = "quiz_discrimination_index_analysis.pdf"
    output_path = output_dir / name

    plt.savefig(output_path)
    plt.close()
    return AnalysisFigure(
        name=name,
        caption=r"""\textbf{Discrimination Index Analysis}: Evaluates how well each question differentiates between high-performing and low-performing students. Calculated as the difference in average scores between the top 25\% and bottom 25\% of students, normalized by the maximum possible score. If D is negative, the question may be flawed as it suggests that lower-performing students are scoring higher on this question than higher-performing students.""",
    )


def make_quiz_analysis(graded_sets: list[GradedSet], out_directory: str | Path):
    out_directory = Path(out_directory)
    out_directory.mkdir(parents=True, exist_ok=True)

    figures = []

    pd_fig = point_distribution_analysis(graded_sets, out_directory)
    figures.append(pd_fig)

    corr_fig = correlation_analysis(graded_sets, out_directory)
    figures.append(corr_fig)

    di_fig = discrimination_index_analysis(graded_sets, out_directory)
    figures.append(di_fig)

    return figures
