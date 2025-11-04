from pathlib import Path
import streamlit as st
from streamlit_shortcuts import add_shortcuts
from mcqpy.question import Question
import pandas as pd

st.title("MCQPy Test Page")

# Add custom CSS for performance and styling
st.markdown(
    """
<style>
div[role="radiogroup"] > label {
    margin-bottom: 10px !important;
    padding-bottom: 5px !important;
}

/* Optimize image loading */
img {
    image-rendering: optimizeSpeed;
    image-rendering: -moz-crisp-edges;
    image-rendering: -webkit-optimize-contrast;
    image-rendering: optimize-contrast;
}

/* Reduce layout shifts */
.stImage > img {
    max-width: 100%;
    height: auto;
}
</style>
""",
    unsafe_allow_html=True,
)

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}


@st.cache_data
def _process_image_captions(image_caption: dict, num_images: int):
    """Cache image caption processing to avoid recomputation"""
    sub_captions = [caption for index, caption in image_caption.items() if index >= 0]

    if len(sub_captions) != num_images:
        for _ in range(num_images - len(sub_captions)):
            sub_captions.append("")

    return sub_captions


def render_question(question: Question, index: int = 1):
    st.header(f"Question {index}")
    st.caption(f"Slug: {question.slug} | QID: {question.qid}")

    if question.image:
        # Cache the caption processing
        sub_captions = _process_image_captions(
            question.image_caption, len(question.image)
        )

        # Use columns for better image loading performance
        if len(question.image) == 1:
            st.image(
                question.image[0],
                width=400,
                caption=sub_captions[0] if sub_captions else None,
            )
        else:
            # For multiple images, use columns for parallel loading
            cols = st.columns(min(len(question.image), 3))  # Max 3 images per row
            for i, img_url in enumerate(question.image):
                col_idx = i % len(cols)
                with cols[col_idx]:
                    caption = sub_captions[i] if i < len(sub_captions) else ""
                    st.image(img_url, caption=caption)

        if question.image_caption.get(-1):
            st.caption(question.image_caption[-1])

    st.write(question.text)

    if question.question_type == "single":
        options = [
            f"({chr(i + 64)}) {choice}"
            for i, choice in enumerate(question.choices, start=1)
        ]

        saved_answer = st.session_state.quiz_answers.get(question.qid)
        default_index = None
        if saved_answer and saved_answer in options:
            default_index = options.index(saved_answer)

        selected = st.radio(
            "Select your answer",
            options=options,
            index=default_index,
            key=f"radio_{question.qid}",
        )

        if selected:
            st.session_state.quiz_answers[question.qid] = selected

        # selected = st.radio("Select your answer", options=options, index=None)
        # st.session_state.quiz_answers[question.qid] = selected

    elif question.question_type == "multiple":
        st.subheader("Select your answers")
        for i, choice in enumerate(question.choices, start=1):
            st.markdown(f"   **({chr(i + 64)})**   {choice}")

        saved_answers = st.session_state.quiz_answers.get(question.qid, [])

        selected = st.multiselect(
            "Select your answers:",
            options=[f"{chr(i + 64)}" for i in range(1, len(question.choices) + 1)],
            default=saved_answers,
            key=f"multi_{question.qid}",
        )

        # Store the answers
        st.session_state.quiz_answers[question.qid] = selected
    else:
        st.error(f"Unknown question type: {question.question_type}")


def grade_quiz(questions: list[Question], answers: dict = None):
    from mcqpy.grade.utils import ParsedSet, ParsedQuestion
    from mcqpy.grade import MCQGrader
    from mcqpy.create.manifest import Manifest, ManifestItem
    from mcqpy.grade.rubric import StrictRubric

    parsed_questions = []
    for question in questions:
        # Find the question by qid
        qid = question.qid
        question_answers = answers.get(qid, None)
        if question_answers is None:
            parsed_questions.append(
                ParsedQuestion(
                    qid=qid,
                    slug=question.slug,
                    answers=None,
                    onehot=[0] * len(question.choices),
                )
            )

        # Convert answer back to indices
        if isinstance(question_answers, str):
            # Single choice
            index = ord(question_answers[1]) - 65  # Convert 'A' to 0, 'B' to 1, etc.
            onehot = [1 if i == index else 0 for i in range(len(question.choices))]
            parsed_questions.append(
                ParsedQuestion(
                    qid=qid, slug=question.slug, answers=[index], onehot=onehot
                )
            )
        elif isinstance(question_answers, list):
            # Multiple choice
            indices = [
                ord(a[0]) - 65 for a in question_answers
            ]  # Convert 'A' to 0, 'B' to 1, etc.
            onehot = [1 if i in indices else 0 for i in range(len(question.choices))]
            parsed_questions.append(
                ParsedQuestion(
                    qid=qid, slug=question.slug, answers=indices, onehot=onehot
                )
            )

    parsed_set = ParsedSet(
        student_id="test_student",
        student_name="Test Student",
        questions=parsed_questions,
    )

    # Construct manifest
    manifest_items = [ManifestItem.from_question(q, None) for q in questions]
    manifest = Manifest(items=manifest_items)

    grader = MCQGrader(manifest=manifest, rubric=StrictRubric())
    graded_set = grader.grade(parsed_set=parsed_set)
    return graded_set

def _show_answer_summary():
    st.title("End of the Quiz")
    st.write("You have reached the end of the quiz. Thank you for participating!")

    # Show the user's answers
    st.subheader("Your Answers Summary")
    for idx, question in enumerate(st.session_state.questions, start=1):
        answer = st.session_state.quiz_answers.get(
            question.qid, "No answer selected"
        )
        st.markdown(f"- Question {idx}: Your answer: {answer}")

    if st.button("Grade Quiz", key="grade_quiz_button"):
        graded = grade_quiz(
            questions=st.session_state.questions,
            answers=st.session_state.quiz_answers,
        )
        st.subheader("Grading Results")

        per_question_points = [g.point_value for g in graded.graded_questions]

        df = pd.DataFrame(
            {
                "Question": [
                    f"Q{idx + 1}" for idx in range(len(graded.graded_questions))
                ],
                "Slug": [g.slug for g in graded.graded_questions],
                "Points Earned": per_question_points,
                "Max Points": [g.max_point_value for g in graded.graded_questions],
            }
        )

        column1, column2 = st.columns(2)

        with column1:
            st.metric(
                label="Total Score", value=f"{graded.points} / {graded.max_points}"
            )

        with column2:
            st.metric(
                label="Percentage",
                value=f"{(graded.points / graded.max_points) * 100:.2f} %",
            )

        tab1, tab2 = st.tabs(["Table View", "Bar Chart View"])
        with tab1:
            st.table(df)
        with tab2:
            st.bar_chart(df.set_index("Question"))

def _upload_questions():
    import yaml

    uploaded_files = st.file_uploader(
        "Upload Questions File", type=["yaml"], accept_multiple_files=True
    )
    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            data = yaml.safe_load(uploaded_file)
            question = Question.model_validate(
                data, context={"base_dir": Path.cwd() / "questions"}
            )
            st.session_state.questions.append(question)


def _load_questions_from_link(link=None):
    from mcqpy.web.utils.remote_loader import load_remote_quiz

    if link is None:
        link = st.text_input("Enter the link to load questions from:")

    # Performance options
    if link:
        loading_msg = "Loading questions from remote repository..."
        with st.spinner(loading_msg):
            quiz_content = load_remote_quiz(link)
            if quiz_content and "questions" in quiz_content:
                st.session_state.questions.extend(quiz_content["questions"])

                # Show different success messages based on loader type
                num_questions = len(quiz_content.get("questions", []))
                if quiz_content.get("loader_type") == "cached":
                    st.success(
                        f"🚀 Successfully downloaded {num_questions} questions and images to local cache!"
                    )
                else:
                    st.success(f"Successfully loaded {num_questions} questions!")
            else:
                st.error("Failed to load questions from the provided link.")


def _load_questions_with_token(token=None, questions=None):
    from mcqpy.web.utils.tokenizer import decode_token
    from mcqpy.web.utils.remote_loader import load_remote_quiz
    token = st.text_input("Enter your access token:")
    if token:
        # Placeholder for actual loading logic
        url = decode_token(token)
        if url:
            # Load questions from the URL
            quiz_content = load_remote_quiz(url)

            if quiz_content and "questions" in quiz_content:
                st.session_state.questions.extend(quiz_content["questions"])




# Upload questions:
# With this:
if "questions" not in st.session_state:
    st.session_state.questions = []


if len(st.session_state.questions) == 0:
    question_loader = st.container()

    with question_loader:
        upload_tab, link_tab, token_tab = st.tabs(
            ["📁  Upload Questions", "🔗  Load link", "🔑  Load with token"]
        )

        with upload_tab:
            _upload_questions()

        with link_tab:
            _load_questions_from_link()

        with token_tab:
            _load_questions_with_token()


if len(st.session_state.questions) != 0:
    n_pages = len(st.session_state.questions) + 2
    # Initialize the question index in session state
    if "quiz_page_idx" not in st.session_state:
        st.session_state.quiz_page_idx = 0

    # Handle button clicks first
    col1, col2, col3 = st.columns(3, vertical_alignment="center", gap="large")

    with col1:
        prev_clicked = st.button(
            "⬅️ Previous Question", width="stretch", key="prev_question_button"
        )

    with col3:
        next_clicked = st.button(
            "Next Question ➡️", width="stretch", key="next_question_button"
        )

    # Update session state after capturing button states
    if prev_clicked:
        st.session_state.quiz_page_idx = max(0, st.session_state.quiz_page_idx - 1)
    if next_clicked:
        st.session_state.quiz_page_idx = min(
            n_pages - 1, st.session_state.quiz_page_idx + 1
        )

    # Now display the progress bar with the updated state
    with col2:
        st.progress(
            st.session_state.quiz_page_idx / (n_pages - 1),
            text=f"{st.session_state.quiz_page_idx} of {n_pages - 1}",
        )

        st.number_input(
            "Jump to Question", min_value=0, max_value=n_pages - 1, key="quiz_page_idx"
        )

    if 1 <= st.session_state.quiz_page_idx <= len(st.session_state.questions):
        render_question(
            question=st.session_state.questions[st.session_state.quiz_page_idx - 1],
            index=st.session_state.quiz_page_idx,
        )

    elif st.session_state.quiz_page_idx == 0:
        st.title("Welcome to the MCQPy Test!")
        st.write("Click 'Next Question' to begin.")
    else:
        _show_answer_summary()

    # Reset button
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.button("Restart quiz", on_click=lambda: st.session_state.update(
            {
                "quiz_page_idx": 0,
                "quiz_answers": {},
            }
        ))

    with col2:
        st.button("🔄 Reload questions", on_click=lambda: st.session_state.update(
            {
                "quiz_page_idx": 0,
                "quiz_answers": {},
                "questions": [],
            }
        ), help="Clear all current questions and answers and reload.")

add_shortcuts(prev_question_button="arrowleft", next_question_button="arrowright")
