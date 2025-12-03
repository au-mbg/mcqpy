from mcqpy.question.question import Question, qid_from_slug
import pytest

### Test cases for Question._derive_qid

def test_derive_qid():
    data = {'slug': 'sample-question'}
    computed_qid = qid_from_slug(data['slug'])
    data = Question._derive_qid(data)
    assert data['qid'] == computed_qid

def test_derive_qid_existing():
    data = {'slug': 'sample-question'}
    computed_qid = qid_from_slug(data['slug'])
    data['qid'] = computed_qid
    data = Question._derive_qid(data)
    assert data['qid'] == computed_qid

def test_derive_qid_mismatch():
    data = {'slug': 'sample-question'}
    data['qid'] = 'different-qid'
    with pytest.raises(ValueError, match="Provided qid does not match slug-derived qid"):
        Question._derive_qid(data)

def test_derive_requires_slug():
    data = {}
    with pytest.raises(ValueError, match="slug is required to derive qid"):
        Question._derive_qid(data)


### Test cases for Question.validate_image        

@pytest.fixture
def info():
    class Info:
        context = {}
    return Info()

@pytest.fixture
def image(question_factory):
    return question_factory.images[0]

def test_validate_image_none(info):
    v = None
    v_out = Question.validate_image(v, info=info)
    assert v_out is None

def test_validate_image_string(image, info):
    v = image
    v_out = Question.validate_image(v, info=info)
    assert v_out[0] == str(v)

def test_validate_image_list(image, info):
    v = [image, image]
    v_out = Question.validate_image(v, info=info)
    assert v_out == [str(image), str(image)]

def test_validate_image_invalid_type(info):
    v = 12345
    with pytest.raises(TypeError):
        Question.validate_image(v, info=info)

def test_validate_image_invalid_extension(info, tmp_path):
    invalid_image_path = tmp_path / "image.txt"
    invalid_image_path.write_text("This is not a valid image file.")
    v = str(invalid_image_path)
    with pytest.raises(ValueError, match="Unsupported image extension"):
        Question.validate_image(v, info=info)

def test_validate_image_nonexistent_file(info):
    v = "nonexistent_image.png"
    with pytest.raises(FileNotFoundError, match="Image not found"):
        Question.validate_image(v, info=info)

def test_validate_image_https(info):
    v = "https://example.com/image.png"
    v_out = Question.validate_image(v, info=info)
    assert v_out[0] == v

### Test cases for Question._normalize_media_fields

@pytest.fixture
def raw_image_data():
    return {
        'image': 'https://example.com/image1.png',
        'image_options': None,
        'image_caption': 'An example image'
    }

def test_normalize_media_fields(raw_image_data):
    data = Question._normalize_media_fields(raw_image_data)
    assert isinstance(data['image'], list)

def test_normalize_media_fields_global_caption(raw_image_data):
    raw_image_data['image_caption'] = {-1: 'Global caption'}
    data = Question._normalize_media_fields(raw_image_data)
    assert data['image_caption'] == {-1: 'Global caption'}

def test_normalize_media_bad_index(raw_image_data):
    raw_image_data['image_caption'] = {5: 'Invalid index caption'}
    with pytest.raises(ValueError, match="contains out-of-range indices"):
        Question._normalize_media_fields(raw_image_data)

### Test cases for Question.validate_code

@pytest.fixture
def raw_code_data():
    return {
        'code': 'print("Hello, World!")',
        'code_language': 'python'
    }

def test_validate_code_string(raw_code_data):
    data = Question.validate_code(raw_code_data)
    assert isinstance(data['code'], list)
    assert data['code'][0] == 'print("Hello, World!")'

def test_validate_code_list(raw_code_data):
    raw_code_data['code'] = ['print("Line 1")', 'print("Line 2")']
    data = Question.validate_code(raw_code_data)
    assert data['code'] == ['print("Line 1")', 'print("Line 2")']

def test_validate_code_language(raw_code_data):
    raw_code_data['code_language'] = ['python', 'javascript']
    data = Question.validate_code(raw_code_data)
    assert data['code_language'] == ['python', 'javascript']

### Test cases for Question.validate_and_normalize_data

def test_vand_year_only():
    out = Question.validate_and_normalize_date('2023')
    assert out == '01/01/2023'

def test_vand_year_bad():
    with pytest.raises(ValueError, match='Year 1883 is outside'):
        Question.validate_and_normalize_date('1883')

def test_vand_full_date():
    out = Question.validate_and_normalize_date('25/12/2020')
    assert out == '25/12/2020'

def test_vand_bad_format():
    with pytest.raises(ValueError):
        Question.validate_and_normalize_date('2020-12-25')

def test_vand_badparts_format():
    with pytest.raises(ValueError):
        Question.validate_and_normalize_date('2020/13/01/02')
