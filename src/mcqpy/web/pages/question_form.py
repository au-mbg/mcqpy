import streamlit as st
from mcqpy.question import Question

def get_field_literal_values(model_class, field_name):
    """Get literal values from a Pydantic model field"""
    try:
        field_info = model_class.model_fields[field_name]
        
        # For Pydantic v2, check the annotation
        if hasattr(field_info, 'annotation'):
            from typing import get_args, get_origin, Literal
            if get_origin(field_info.annotation) is Literal:
                return list(get_args(field_info.annotation))
                
        # Alternative: check constraints if available
        if hasattr(field_info, 'constraints'):
            constraints = field_info.constraints
            if constraints and hasattr(constraints, 'choices'):
                return list(constraints.choices)
                
    except (KeyError, AttributeError):
        pass
    
    return []

def show():
    st.title("❓ Question Form")

    question_text = st.text_area("Enter question text")
    question_type = st.selectbox("Select Question Type", options=get_field_literal_values(Question, "question_type"), help="Choose between single or multiple choice question types")

    slug = st.text_input("Enter Question Slug", value="example_question", help="A unique identifier for the question")
    number_of_options = st.number_input("Number of Options", min_value=2, max_value=10, value=4, step=1)

    if number_of_options:
        options = []
        for i in range(number_of_options):
            option_text = st.text_input(f"Option {i + 1} text", help=f"Text for option {i + 1}")
            options.append(option_text)

    if question_type == "single":
        correct_answer = st.selectbox("Select the correct answer", options=[f"Option {i + 1}" for i in range(number_of_options)])
    elif question_type == "multiple":
        correct_answer = st.multiselect("Select the correct answers", options=[f"Option {i + 1}" for i in range(number_of_options)])

    point_value = st.number_input("Point Value", min_value=0, value=1, step=1)

    try:
        question = Question(
            text=question_text,
            choices=options,
            slug=slug,
            correct_answers=[int(ans.split()[-1]) - 1 for ans in (correct_answer if isinstance(correct_answer, list) else [correct_answer])],
            question_type=question_type,
            point_value=point_value
        )
        question

        st.download_button(
            label="Download Question as YAML",
            data=question.as_yaml(),
            file_name=f"{slug}.yaml",
        )
    except Exception as e:
        st.error(f"Error creating question: {e}")
        return


if __name__ == "__main__":
    show()
