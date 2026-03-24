from mcqpy.question import Question
from mcqpy.web import (
    WebQuizBundle,
    build_web_quiz_bundle,
    decode_quiz_token,
    encode_quiz_token,
)

def test_smoke():
    question1 = Question(
        slug='test-question',
        text='What is 2 + 2?',
        choices=['3', '4', '5'],
        correct_answers=[1],
        question_type='single',

    )
    print(question1)

    bundle = build_web_quiz_bundle([question1], title="Smoke test")
    assert isinstance(bundle, WebQuizBundle)

    token = encode_quiz_token("https://example.com/quiz.json")
    assert decode_quiz_token(token) == "https://example.com/quiz.json"

test_smoke()
