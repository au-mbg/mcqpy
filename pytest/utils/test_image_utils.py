from mcqpy.utils.image import check_if_url, get_url_image_suffix, check_and_download_tmp, download_image, convert_image
import pytest
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ImageTestCase:
    input_url: str
    expected_suffix: str
    is_url: bool


@pytest.fixture(params=[
    ImageTestCase(input_url="http://example.com/image.jpg", expected_suffix=".jpg", is_url=True),
    ImageTestCase(input_url="https://example.com/image.png", expected_suffix=".png", is_url=True),
    ImageTestCase(input_url="/local/path/image.gif", expected_suffix=".gif", is_url=False),
    ImageTestCase(input_url=Path("C:/images/photo.tiff"), expected_suffix=".tiff", is_url=False),
    ImageTestCase(input_url="not_a_url_or_path", expected_suffix=None, is_url=False),
])
def url_image_testcase(request) -> ImageTestCase:
    return request.param


def test_check_if_url_true(url_image_testcase):
    assert check_if_url(url_image_testcase.input_url) is url_image_testcase.is_url


def test_get_url_image_suffix(url_image_testcase):
    assert get_url_image_suffix(url_image_testcase.input_url) == url_image_testcase.expected_suffix

def test_download_image(url_image_testcase, tmp_path, mocker):
    if url_image_testcase.is_url:
        save_path = tmp_path / "downloaded_image"
        mock_response = mocker.MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'test image data'
        mocker.patch('requests.get', return_value=mock_response)

        downloaded_path = download_image(url_image_testcase.input_url, str(save_path))
        assert downloaded_path.exists()
        assert downloaded_path.suffix == url_image_testcase.expected_suffix

def test_convert_image(tmp_path):
    from PIL import Image

    # Create a sample image to convert
    original_image_path = tmp_path / "original.jpg"
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(original_image_path)

    # Convert the image
    convert_image(original_image_path)

    # Check if the converted image exists and is in PNG format
    converted_image_path = original_image_path.with_suffix('.png')
    assert converted_image_path.exists()
    with Image.open(converted_image_path) as converted_img:
        assert converted_img.format == 'PNG'

def test_convert_image_RGBA(tmp_path):
    from PIL import Image

    # Create a sample RGBA image to convert
    original_image_path = tmp_path / "original.png"
    img = Image.new('RGBA', (100, 100), color = (255, 0, 0, 128))
    img.save(original_image_path)

    # Convert the image
    convert_image(original_image_path)

    # Check if the converted image exists and is in PNG format
    converted_image_path = original_image_path.with_suffix('.png')
    assert converted_image_path.exists()
    with Image.open(converted_image_path) as converted_img:
        assert converted_img.format == 'PNG'

def test_convert_image_P(tmp_path):
    from PIL import Image

    # Create a sample P mode image to convert
    original_image_path = tmp_path / "original.gif"
    img = Image.new('P', (100, 100))
    img.save(original_image_path)

    # Convert the image
    convert_image(original_image_path)

    # Check if the converted image exists and is in PNG format
    converted_image_path = original_image_path.with_suffix('.png')
    assert converted_image_path.exists()
    with Image.open(converted_image_path) as converted_img:
        assert converted_img.format == 'PNG'

def test_convert_image_grayscale(tmp_path):
    from PIL import Image

    # Create a sample grayscale (L mode) image to convert
    original_image_path = tmp_path / "original_gray.jpg"
    img = Image.new('L', (100, 100), color=128)  # Gray image
    img.save(original_image_path)

    # Convert the image
    convert_image(original_image_path)

    # Check if the converted image exists and is in PNG format
    converted_image_path = original_image_path.with_suffix('.png')
    assert converted_image_path.exists()
    with Image.open(converted_image_path) as converted_img:
        assert converted_img.format == 'PNG'
        assert converted_img.mode == 'RGB'

def test_check_and_download_tmp(tmp_path, mocker):
    from PIL import Image
    from io import BytesIO

    url = "http://example.com/test_image.png"
    img = Image.new('RGB', (10, 10), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.content = img_bytes.read()    
    mocker.patch('requests.get', return_value=mock_response)

    result_path = check_and_download_tmp(url, tmp_path)

    assert result_path.exists()
    assert result_path.suffix == '.png'
