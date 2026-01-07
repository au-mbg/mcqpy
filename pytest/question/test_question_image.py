import pytest
from mcqpy.question import Question
from pathlib import Path

from importlib.resources import files

SRC_DIRECTORY = files("mcqpy").parent.parent 

@pytest.fixture()
def question_with_image(question_factory):
    question = question_factory(image=True)
    return question

@pytest.fixture()
def question_with_image_on_disk(question_with_image, tmp_path):
    path = tmp_path / 'question_with_image.yaml'
    question_with_image.save(path)
    return path


@pytest.fixture()
def question_with_multiple_images(question_factory):
    question = question_factory(image=3)
    return question


def test_question_with_image_initialization(question_with_image):
    assert len(question_with_image.image) == 1

def test_image_exists(question_with_image):
    assert Path(question_with_image.image[0]).exists()

def test_question_with_multiple_images_initialization(question_with_multiple_images):
    assert len(question_with_multiple_images.image) == 3

def test_multiple_images_exist(question_with_multiple_images):
    for img_path in question_with_multiple_images.image:
        print(img_path)
        assert Path(img_path).exists()

def test_question_image_save(question_with_image, tmp_path):
    question_with_image.save(tmp_path / 'question.yaml')

def test_question_image_load(question_with_image_on_disk):
    loaded_question = Question.load_yaml(question_with_image_on_disk)
    assert len(loaded_question.image) == 1
    assert Path(loaded_question.image[0]).exists()
    loaded_question.save(question_with_image_on_disk.parent / 're_saved_question.yaml')

