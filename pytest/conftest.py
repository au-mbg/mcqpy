from pathlib import Path
from importlib.resources import files
from mcqpy.question import Question
from dataclasses import dataclass
import pytest
import shutil
from mcqpy.compile import MultipleChoiceQuiz, FrontMatterOptions, HeaderFooterOptions

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_latex: mark test as requiring LaTeX installation"
    )

def pytest_runtest_setup(item):
    """Automatically skip tests marked with requires_latex if LaTeX is not available"""
    if "requires_latex" in item.keywords:
        if not shutil.which("pdflatex"):
            pytest.skip("LaTeX (pdflatex) is not installed")
            

@dataclass
class CodeSnippet:
    language: str
    content: str


class QuestionFactory:
    ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".tif", ".tiff"}

    def __init__(self):
        self.resource_directory = files("mcqpy").parent.parent / "pytest" / "resources"
        self.index = -1

    @property
    def images(self):
        if not hasattr(self, "_images"):
            image_dir = self.resource_directory / "images"
            self._images = [
                f
                for f in image_dir.glob("*")
                if f.suffix.lower() in self.ALLOWED_IMAGE_EXTS
            ]
        return self._images

    @property
    def code_snippets(self):
        if not hasattr(self, "_code_snippets"):
            code_dir = self.resource_directory / "code_snippets"
            paths = [f for f in code_dir.glob("*.py")]
            self._code_snippets = []
            for path in paths:
                with open(path, "r") as f:
                    self._code_snippets.append(
                        CodeSnippet(language="python", content=f.read())
                    )
        return self._code_snippets

    def get_index(self):
        self.index += 1
        return self.index

    def generate_question(
        self, image: bool | int = False, code: bool | int = False
    ) -> Question:
        index = self.get_index()
        slug = f"sample-question-{index}"
        question_text = f"This is sample question {index}?"
        choices = [f"Choice {i}" for i in range(1, 5)]
        question_type = "single" if index % 2 == 0 else "multiple"
        correct_choice = [index % len(choices)]


        ## Get some images
        if image:
            images = []
            if isinstance(image, int) and image > 1:
                captions = {-1: f"This is the caption for the whole {index}."}
                options = {}
                for i in range(image):
                    img = self.images[(index + i) % len(self.images)]
                    images.append(str(img))
                    captions[i] = f"This is the caption for image {index + i}."
                    if i % 2 == 0:
                        options[i] = {"width": "0.5\\textwidth", "newline": True}
                    else:
                        options[i] = {"width": "0.5\\textwidth"}

            else:
                img = self.images[index % len(self.images)]
                images.append(str(img))
                options = {0: {"width": "0.5\\textwidth"}}
                captions = {0: f"This is the caption for image {index}."}
        else: 
            images = None
            captions = None
        
        ## Get some code snippets
        if code:
            snippets = []
            if isinstance(code, int):
                for i in range(code):
                    snip = self.code_snippets[(index + i) % len(self.code_snippets)]
                    snippets.append(snip)
            else:
                snippets = [self.code_snippets[index % len(self.code_snippets)]]
            
            snippet_code = [s.content for s in snippets]
            snippet_language = [s.language for s in snippets]
        else:
            snippet_code = None
            snippet_language = None

        question_data = dict(
            slug=slug,
            text=question_text,
            choices=choices,
            correct_answers=correct_choice,
            question_type=question_type,
            image=images if image else None,
            image_caption=captions if image else None,
            image_options=options if image else None,
            code=snippet_code,
            code_language=snippet_language,
            explanation="This is the explanation for the question.",
            created_date="01/01/2024",
        )

        question = Question.model_validate(question_data, context={})

        return question
    
    def __call__(self, image: bool | int = False, code: bool | int = False) -> Question:
        return self.generate_question(image=image, code=code)
    

@pytest.fixture(scope="session")
def question_factory():
    return QuestionFactory()

@pytest.fixture(scope="session")
def question_set(question_factory):
    n_questions = 20
    image = [0 for _ in range(n_questions)]
    code = [0 for _ in range(n_questions)]
    image[0] = True
    image[1] = 2
    code[2] = True
    code[3] = 2
    image[4] = True
    code[4] = True
    image[5] = 2
    code[5] = 2
    questions = [question_factory(image=image[i], code=code[i]) for i in range(0, 20)]
    return questions

@pytest.fixture(scope="session", params=['full', 'empty'])
def header_options(request) -> HeaderFooterOptions:
    case = request.param
    if case == 'full':
        return HeaderFooterOptions(
            header_left="Left Header",
            header_center="Center Header",
            header_right="Right Header",
            footer_left="Left Footer",
            footer_center="Center Footer",
            footer_right="Right Footer"
        )
    else:  # empty
        return HeaderFooterOptions(header_left=None, header_center=None, header_right=None,
                                   footer_left=None, footer_center=None, footer_right=None)

@pytest.fixture(scope="session", params=[True, False])
def front_matter_options(request) -> FrontMatterOptions:
    return FrontMatterOptions(
        title="Sample Quiz",
        author="Test Author",
        date="2024-01-01" if request.param else True,
        id_fields=request.param,
        exam_information="This is a sample exam."
    )

@pytest.fixture(scope="session")
def mcq(tmp_path_factory, question_set, header_options, front_matter_options) -> MultipleChoiceQuiz:
    tmp_path = tmp_path_factory.mktemp("mcq_build_test")
    path = tmp_path / "test_quiz.pdf"
    mcq = MultipleChoiceQuiz(file=path, questions=question_set, front_matter=front_matter_options, header_footer=header_options)

    return mcq

@pytest.fixture(scope="session")
def built_mcq(mcq):
    mcq.build(generate_pdf=True)
    return mcq

