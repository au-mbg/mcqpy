"""
Remote Quiz Loader

Handles loading quiz configurations and questions from remote sources
like GitHub repositories or zip archives.
"""

from pathlib import Path
from typing import Dict, Optional

import yaml
from mcqpy.web.utils.remote_loader.base_loader import RemoteLoader
import shutil
import tarfile
import tempfile
import zipfile

class ArchiveLoader(RemoteLoader):
    """Loader for zip and tar.gz archives"""

    def can_handle(self, url: str) -> bool:
        """Check if URL is an archive"""
        return (
            url.endswith((".zip", ".tar.gz"))
            or "/blob/" in url
            and url.endswith((".zip", ".tar.gz"))
        )

    def load_quiz(self, url: str) -> Optional[Dict]:
        """Load quiz files from an archive"""
        try:
            # Convert GitHub blob URLs to raw URLs if needed
            download_url = self._convert_to_raw_url(url)

            # Download the archive
            response = self.session.get(download_url)
            response.raise_for_status()

            # Create persistent cache directory for this quiz
            persistent_cache_dir = Path(tempfile.mkdtemp(prefix="mcqpy_archive_cache_"))

            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Determine archive type and file name
                if download_url.endswith(".tar.gz"):
                    archive_path = Path(temp_dir) / "archive.tar.gz"
                    archive_path.write_bytes(response.content)
                    self._extract_tar_gz(archive_path, temp_dir)
                else:  # .zip
                    archive_path = Path(temp_dir) / "archive.zip"
                    archive_path.write_bytes(response.content)
                    self._extract_zip(archive_path, temp_dir)

                # Find config.yaml and questions directory
                config_data = None
                questions = {}
                quiz_root_dir = None

                print(f"Scanning extracted files in: {temp_dir}")
                for root, dirs, files in (Path(temp_dir)).walk():
                    print(f"Found directory: {root}")
                    print(f"  Subdirectories: {dirs}")
                    print(f"  Files: {files}")

                    if "config.yaml" in files:
                        config_path = root / "config.yaml"
                        quiz_root_dir = root
                        print(f"Found config.yaml at: {config_path}")
                        try:
                            with open(config_path, "r", encoding="utf-8") as f:
                                config_data = yaml.safe_load(f)
                        except Exception as e:
                            print(f"Failed to read config.yaml: {e}")

                    if "questions" in dirs:
                        questions_dir = root / "questions"
                        if quiz_root_dir is None:
                            quiz_root_dir = root
                        print(f"Found questions directory at: {questions_dir}")
                        questions = self._load_questions_from_local_dir(questions_dir)

                # Config is optional - we can still proceed without it
                if not questions:
                    # No questions found - this is an error
                    print("No questions directory found in the archive")
                    return None

                # Copy the entire quiz structure to persistent cache
                if quiz_root_dir:
                    print(
                        f"Copying quiz files from {quiz_root_dir} to {persistent_cache_dir}"
                    )
                    # Copy all files and subdirectories from quiz root to cache
                    for item in quiz_root_dir.iterdir():
                        if item.is_dir():
                            shutil.copytree(
                                item,
                                persistent_cache_dir / item.name,
                                dirs_exist_ok=True,
                            )
                        else:
                            shutil.copy2(item, persistent_cache_dir / item.name)
                else:
                    # Fallback: copy entire temp directory
                    print(
                        f"No specific quiz root found, copying entire extraction to {persistent_cache_dir}"
                    )
                    for item in Path(temp_dir).iterdir():
                        if item.is_dir():
                            shutil.copytree(
                                item,
                                persistent_cache_dir / item.name,
                                dirs_exist_ok=True,
                            )
                        else:
                            shutil.copy2(item, persistent_cache_dir / item.name)

                return {
                    "config": config_data,
                    "questions": questions,
                    "source_url": url,
                    "cache_dir": str(persistent_cache_dir),
                }
        except Exception as e:
            # st.error(f"Failed to load quiz from archive: {str(e)}")
            raise e

    def _convert_to_raw_url(self, url: str) -> str:
        """Convert GitHub blob URL to raw download URL"""
        if "/blob/" in url and "github.com" in url:
            # Convert github.com/.../blob/branch/... to raw.githubusercontent.com/.../branch/...
            return url.replace("github.com", "raw.githubusercontent.com").replace(
                "/blob/", "/"
            )
        return url

    def _extract_zip(self, archive_path: Path, temp_dir: str) -> None:
        """Extract ZIP archive"""
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

    def _extract_tar_gz(self, archive_path: Path, temp_dir: str) -> None:
        """Extract tar.gz archive"""
        with tarfile.open(archive_path, "r:gz") as tar_ref:
            # Use filter='data' for Python 3.14 compatibility
            try:
                tar_ref.extractall(temp_dir, filter="data")
            except TypeError:
                # Fallback for older Python versions that don't support filter
                tar_ref.extractall(temp_dir)

    def _load_questions_from_local_dir(self, questions_dir: Path) -> Dict[str, Dict]:
        """Load question files from local directory and convert image paths to data URLs"""
        questions = {}

        try:
            # First, load all questions - skip macOS metadata files
            for yaml_file in questions_dir.glob("*.yaml"):
                # Skip Apple metadata files (starting with ._)
                if yaml_file.name.startswith("._"):
                    continue

                try:
                    with open(yaml_file, "r", encoding="utf-8") as f:
                        questions[yaml_file.name] = yaml.safe_load(f)
                except UnicodeDecodeError:
                    # Try with latin-1 encoding as fallback
                    try:
                        with open(yaml_file, "r", encoding="latin-1") as f:
                            questions[yaml_file.name] = yaml.safe_load(f)
                    except Exception as e:
                        print(f"Failed to read {yaml_file.name}: {e}")
                        continue
                except Exception as e:
                    print(f"Failed to parse YAML in {yaml_file.name}: {e}")
                    continue

            # Find all image files in the same directory
            image_files = []
            for img_ext in ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg"]:
                image_files.extend(questions_dir.glob(img_ext))
        except Exception:
            # st.error(f"Failed to load questions from directory")
            raise

        return questions

if __name__ == "__main__":
    loader = ArchiveLoader()
    test_url = "https://github.com/au-mbg/mcqpy/blob/main/web_quiz/test_quiz.tar.gz"

    data = loader.load_quiz(test_url)

    for question_file, question_data in data["questions"].items():
        image = question_data.get("image", None)
        if image:
            for img in image if isinstance(image, list) else [image]:
                print(f"Question: {question_file}, Img: {img[:30]}...")

    
