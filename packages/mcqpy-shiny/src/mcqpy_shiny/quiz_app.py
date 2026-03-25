"""Shared quiz app factory used by local and Shinylive runtimes."""

from __future__ import annotations

import traceback

from shiny import App, reactive, render, ui

from .app_types import BundleGrader, BundleLoader, TokenDecoder
from .styles import MATHJAX_BOOTSTRAP, MATHJAX_HEAD, build_css
from .views import (
    answer_input_id,
    render_error_card,
    render_load_panel,
    render_question_card,
    render_results_card,
    render_review_card,
)


def create_quiz_app(
    *,
    load_bundle: BundleLoader,
    decode_token: TokenDecoder,
    grade_bundle: BundleGrader,
    missing_bundle_message: str,
    fixed_url: str | None = None,
    fixed_token: str | None = None,
    allow_manual_load: bool = True,
    title: str = "MCQPy Quiz",
    card_width: str = "900px",
) -> App:
    app_ui = ui.page_fillable(
        ui.head_content(
            ui.tags.script(MATHJAX_HEAD),
            ui.tags.script(src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"),
            ui.tags.style(build_css(card_width)),
            ui.tags.script(MATHJAX_BOOTSTRAP),
        ),
        ui.div(
            ui.h1(title),
            ui.output_ui("load_panel"),
            ui.hr(),
            ui.output_ui("content"),
            class_="mcqpy-shell",
        ),
    )

    def server(input, output, session):
        bundle = reactive.value(None)
        answers = reactive.value({})
        current_index = reactive.value(0)
        load_error = reactive.value(None)
        result = reactive.value(None)
        result_error = reactive.value(None)
        auto_loaded = reactive.value(False)

        def _bundle() -> dict | None:
            return bundle.get()

        def _current_questions() -> list[dict]:
            loaded = _bundle()
            return [] if loaded is None else loaded["questions"]

        def _store_current_answer() -> None:
            loaded = _bundle()
            if loaded is None:
                return

            index = current_index.get()
            questions = loaded["questions"]
            if not (0 <= index < len(questions)):
                return

            input_id = answer_input_id(index)
            current_value = input[input_id]()
            next_answers = dict(answers.get())
            next_answers[questions[index]["qid"]] = current_value
            answers.set(next_answers)

        async def _load_source(source: str) -> None:
            if not source:
                load_error.set("Provide a quiz bundle URL, token, or local path.")
                return

            try:
                loaded = await load_bundle(source)
            except Exception as exc:
                load_error.set(str(exc))
                bundle.set(None)
                result.set(None)
                result_error.set(None)
                return

            load_error.set(None)
            bundle.set(loaded)
            answers.set({})
            result.set(None)
            result_error.set(None)
            current_index.set(0)

        @reactive.effect
        async def _auto_load_fixed_bundle():
            if auto_loaded.get():
                return

            source = None
            if fixed_token:
                source = decode_token(fixed_token)
            elif fixed_url:
                source = fixed_url

            if source is None:
                return

            auto_loaded.set(True)
            await _load_source(source)

        @reactive.effect
        @reactive.event(input.load_link)
        async def _load_link():
            await _load_source(input.quiz_url().strip())

        @reactive.effect
        @reactive.event(input.load_token)
        async def _load_token():
            token = input.quiz_token().strip()
            try:
                source = decode_token(token)
            except ValueError as exc:
                load_error.set(str(exc))
                return
            await _load_source(source)

        @reactive.effect
        @reactive.event(input.next_question)
        def _next_question():
            _store_current_answer()
            questions = _current_questions()
            if questions:
                current_index.set(min(len(questions), current_index.get() + 1))

        @reactive.effect
        @reactive.event(input.prev_question)
        def _prev_question():
            _store_current_answer()
            current_index.set(max(0, current_index.get() - 1))

        @reactive.effect
        @reactive.event(input.jump_slider)
        def _jump_from_slider():
            loaded = _bundle()
            if loaded is None:
                return
            _store_current_answer()
            target = input.jump_slider()
            if target is None:
                return
            current_index.set(min(max(target - 1, 0), len(loaded["questions"])))

        @reactive.effect
        @reactive.event(input.jump_number)
        def _jump_from_number():
            loaded = _bundle()
            if loaded is None:
                return
            _store_current_answer()
            target = input.jump_number()
            if target is None:
                return
            current_index.set(min(max(target - 1, 0), len(loaded["questions"])))

        @reactive.effect
        @reactive.event(input.jump_grid)
        def _jump_from_grid():
            loaded = _bundle()
            if loaded is None:
                return
            _store_current_answer()
            target = input.jump_grid()
            if target is None:
                return
            current_index.set(min(max(int(target) - 1, 0), len(loaded["questions"])))

        @reactive.effect
        @reactive.event(input.submit_quiz)
        def _submit_quiz():
            loaded = _bundle()
            if loaded is None:
                return
            _store_current_answer()
            try:
                graded = grade_bundle(loaded, answers.get())
            except Exception:
                result.set(None)
                result_error.set(traceback.format_exc())
                return

            result_error.set(None)
            result.set(graded)

        @reactive.effect
        @reactive.event(input.restart_quiz)
        def _restart_quiz():
            answers.set({})
            result.set(None)
            result_error.set(None)
            current_index.set(0)

        @output
        @render.ui
        def load_panel():
            return render_load_panel(
                bundle_loaded=_bundle() is not None,
                fixed_url=fixed_url,
                fixed_token=fixed_token,
                allow_manual_load=allow_manual_load,
            )

        @output
        @render.ui
        def content():
            if load_error.get():
                return ui.p(load_error.get(), class_="text-danger")

            if result_error.get():
                return render_error_card(result_error.get())

            loaded = _bundle()
            if loaded is None:
                return ui.markdown(missing_bundle_message)

            if result.get() is not None:
                graded = result.get()
                try:
                    return render_results_card(loaded, graded)
                except Exception:
                    result_error.set(traceback.format_exc())
                    return render_error_card(result_error.get())

            questions = loaded["questions"]
            index = current_index.get()

            if index >= len(questions):
                return render_review_card(questions, answers.get(), index)

            return render_question_card(
                loaded=loaded,
                answers=answers.get(),
                index=index,
                title=title,
            )

    return App(app_ui, server)
