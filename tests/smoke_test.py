from mcqpy.question import Question

def test_smoke():
    question1 = Question(
        slug='test-question',
        text='What is 2 + 2?',
        choices=['3', '4', '5'],
        correct_answers=['4'],
        question_type='single',

    )
    print(question1)

test_smoke()
