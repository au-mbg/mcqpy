import pytest
from mcqpy.question import Question
from pathlib import Path

from importlib.resources import files

SRC_DIRECTORY = files("mcqpy").parent.parent 

@pytest.fixture()
def question_with_image():

    image_path = SRC_DIRECTORY / 'pytest' / 'question' / 'images' / 'dog.png'

    question_data = dict(
        slug="image-question",
        text="Identify the animal in the image.",
        choices=["Cat", "Dog", "Rabbit", "Hamster"],
        correct_answers=[1],
        question_type="single",
        image=str(image_path),
    )

    question = Question.model_validate(question_data, context={})

    return question

@pytest.fixture()
def question_with_multiple_images():

    image_paths = [
        SRC_DIRECTORY / 'pytest' / 'question' / 'images' / 'apple.jpg',
        SRC_DIRECTORY / 'pytest' / 'question' / 'images' / 'cherry.jpg',
    ]

    question_data = dict(
        slug="multi-image-question",
        text="Identify the fruits in the images.",
        choices=["Apple", "Banana", "Cherry", "Date"],
        correct_answers=[0, 2],
        question_type="multiple",
        image=[str(image_paths[0]), str(image_paths[1])],
    )

    question = Question.model_validate(question_data, context={})

    return question


def test_question_with_image_initialization(question_with_image):
    assert question_with_image.slug == "image-question"

def test_image_exists(question_with_image):
    assert Path(question_with_image.image[0]).exists()

def test_question_with_multiple_images_initialization(question_with_multiple_images):
    assert question_with_multiple_images.slug == "multi-image-question"

def test_multiple_images_exist(question_with_multiple_images):
    for img_path in question_with_multiple_images.image:
        print(img_path)
        assert Path(img_path).exists()

