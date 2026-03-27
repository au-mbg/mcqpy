"""UI helpers for quiz rendering."""

from __future__ import annotations

from html import escape

from shiny import ui


def answer_input_id(index: int) -> str:
    return f"answer_{index}"


def _choice_map(choices: list[str]) -> dict[str, str]:
    return {
        chr(65 + index): f"({chr(65 + index)}) {choice}"
        for index, choice in enumerate(choices)
    }


def render_question_media(question: dict) -> list:
    media = []
    captions = question.get("image_captions", {})

    for index, image in enumerate(question.get("images", [])):
        media.append(ui.img(src=image, style="max-width: 100%; height: auto;"))
        caption = captions.get(str(index), captions.get(index))
        if caption:
            media.append(ui.p(caption, class_="text-muted"))

    shared_caption = captions.get("-1", captions.get(-1))
    if shared_caption:
        media.append(ui.p(shared_caption, class_="text-muted"))

    for block in question.get("code_blocks", []):
        media.append(
            ui.tags.pre(
                ui.tags.code(
                    block.get("code", ""),
                    **{"data-language": block.get("language") or "text"},
                )
            )
        )
    return media


def question_answer_ui(question: dict, index: int):
    input_id = answer_input_id(index)
    choices = _choice_map(question["choices"])
    if question["question_type"] == "single":
        return ui.input_radio_buttons(input_id, "Select your answer", choices=choices)
    return ui.input_checkbox_group(input_id, "Select your answers", choices=choices)


def result_chart_svg(questions: list[dict], graded: dict) -> ui.HTML:
    width = 760
    row_height = 30
    top = 28
    left = 92
    right = 58
    bottom = 36
    plot_width = width - left - right
    height = top + bottom + row_height * max(len(graded["question_results"]), 1)
    max_points = max((item["max_points"] for item in graded["question_results"]), default=1)

    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="auto" role="img" aria-label="Points by question">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
        f'<line x1="{left}" y1="{top - 8}" x2="{left}" y2="{height - bottom + 4}" stroke="#c9d2dc" stroke-width="1"/>',
    ]

    for idx, (question, item) in enumerate(zip(questions, graded["question_results"], strict=False)):
        y = top + idx * row_height
        bar_width = 0 if max_points == 0 else (item["points"] / max_points) * plot_width
        max_width = 0 if max_points == 0 else (item["max_points"] / max_points) * plot_width
        label = escape(str(idx + 1))
        title = escape(question["slug"])

        parts.extend(
            [
                f'<title>{title}</title>',
                f'<text x="{left - 10}" y="{y + 17}" text-anchor="end" font-size="13" fill="#334155">{label}</text>',
                f'<rect x="{left}" y="{y + 4}" rx="6" ry="6" width="{max_width}" height="18" fill="#e9eef4"/>',
                f'<rect x="{left}" y="{y + 4}" rx="6" ry="6" width="{bar_width}" height="18" fill="#3b82f6"/>',
                f'<text x="{left + max_width + 8}" y="{y + 18}" font-size="12" fill="#475569">{item["points"]}/{item["max_points"]}</text>',
            ]
        )

    for tick in range(max_points + 1):
        x = left + (0 if max_points == 0 else (tick / max_points) * plot_width)
        parts.extend(
            [
                f'<line x1="{x}" y1="{top - 8}" x2="{x}" y2="{height - bottom + 4}" stroke="#f1f5f9" stroke-width="1"/>',
                f'<text x="{x}" y="{height - 10}" text-anchor="middle" font-size="12" fill="#64748b">{tick}</text>',
            ]
        )

    parts.append("</svg>")
    return ui.HTML("".join(parts))


def question_overview_grid(questions: list[dict], answers: dict, current_index: int):
    buttons = []
    for idx, question in enumerate(questions):
        saved = answers.get(question["qid"])
        is_answered = saved not in (None, [], ())
        classes = ["mcqpy-overview-button"]
        if is_answered:
            classes.append("is-answered")
        if idx == current_index:
            classes.append("is-current")

        buttons.append(
            ui.tags.button(
                ui.tags.span(str(idx + 1), class_="mcqpy-overview-number"),
                type="button",
                onclick=f"Shiny.setInputValue('jump_grid', {idx + 1}, {{priority: 'event'}})",
                class_=" ".join(classes),
                title=question["slug"],
            )
        )

    return ui.div(*buttons, class_="mcqpy-overview-grid")


def render_error_card(error_text: str):
    return ui.card(
        ui.h2("Grading Error"),
        ui.tags.pre(error_text),
        ui.input_action_button("restart_quiz", "Restart quiz"),
        class_="mcqpy-card",
    )


def render_load_panel(
    *,
    bundle_loaded: bool,
    fixed_url: str | None,
    fixed_token: str | None,
    allow_manual_load: bool,
):
    if bundle_loaded:
        return ui.div()

    if fixed_url or fixed_token:
        if not allow_manual_load:
            return ui.div()
        helper = "A fixed quiz is configured for this app, or you can load another one."
    else:
        helper = "Load a quiz bundle from a public link or an obfuscated token."

    return ui.card(
        ui.p(helper),
        ui.row(
            ui.column(
                6,
                ui.input_text("quiz_url", "Quiz bundle URL", placeholder="https://.../quiz.json"),
                ui.input_action_button("load_link", "Load from link"),
            ),
            ui.column(
                6,
                ui.input_text("quiz_token", "Obfuscated token", placeholder="mcqpy:..."),
                ui.input_action_button("load_token", "Load from token"),
            ),
        ),
        class_="mcqpy-card",
    )


def render_results_card(loaded: dict, graded: dict):
    summary = [
        ui.h2("Results"),
        ui.p(f"Score: {graded['points']} / {graded['max_points']}"),
        ui.div(
            ui.h3("Points by question"),
            result_chart_svg(loaded["questions"], graded),
            ui.p(
                "Bars show earned points for each question number; hover labels reflect the full slug.",
                class_="text-muted",
            ),
            class_="mcqpy-results-chart",
        ),
        ui.tags.ul(
            *[
                ui.tags.li(f"{question['slug']}: {item['points']}/{item['max_points']}")
                for question, item in zip(
                    loaded["questions"], graded["question_results"], strict=False
                )
            ]
        ),
        ui.input_action_button("restart_quiz", "Restart quiz"),
    ]
    return ui.card(*summary, class_="mcqpy-card")


def render_review_card(questions: list[dict], answers: dict, index: int):
    items = []
    for question in questions:
        saved = answers.get(question["qid"])
        items.append(
            ui.tags.li(
                f"{question['slug']}: {saved if saved not in (None, [], ()) else 'No answer selected'}"
            )
        )

    return ui.card(
        ui.h2("Review"),
        ui.p("Submit the quiz when you are ready."),
        question_overview_grid(questions, answers, index),
        ui.tags.ul(*items),
        ui.row(
            ui.column(6, ui.input_action_button("prev_question", "Previous question")),
            ui.column(6, ui.input_action_button("submit_quiz", "Submit and grade")),
        ),
        class_="mcqpy-card mcqpy-math",
    )


def render_question_card(loaded: dict, answers: dict, index: int, title: str):
    questions = loaded["questions"]
    question = questions[index]
    progress = f"Question {index + 1} of {len(questions)}"
    question_kind = (
        "Single answer" if question["question_type"] == "single" else "Multiple answers"
    )

    body = [
        ui.h2(loaded.get("metadata", {}).get("title", title)),
        ui.p(progress, class_="text-muted"),
        ui.row(
            ui.column(
                8,
                ui.input_slider(
                    "jump_slider",
                    "Jump to question",
                    min=1,
                    max=len(questions) + 1,
                    value=index + 1,
                    step=1,
                    width="100%",
                ),
            ),
            ui.column(
                4,
                ui.input_numeric(
                    "jump_number",
                    "Question number",
                    value=index + 1,
                    min=1,
                    max=len(questions) + 1,
                    width="100%",
                ),
            ),
            class_="mcqpy-jump-row",
        ),
        ui.h3(question["slug"]),
        ui.p(
            f"{question_kind} • {question['point_value']} point"
            f"{'' if question['point_value'] == 1 else 's'}",
            class_="mcqpy-question-meta",
        ),
        ui.div(ui.markdown(question["text"]), class_="mcqpy-question-text"),
        ui.div(*render_question_media(question), class_="mcqpy-media"),
        ui.div(question_answer_ui(question, index), class_="mcqpy-answer-group"),
        ui.row(
            ui.column(4, ui.input_action_button("prev_question", "Previous")),
            ui.column(4, ui.input_action_button("next_question", "Next")),
            ui.column(4, ui.div()),
            class_="mcqpy-nav-row",
        ),
        question_overview_grid(questions, answers, index),
    ]
    return ui.card(*body, class_="mcqpy-card mcqpy-math")
