import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

import yaml

from mcqpy.web.utils.remote_loader.base_loader import RemoteLoader


class CachedGitHubLoader(RemoteLoader):
    """GitHub loader that downloads questions and images to a temporary directory for local access"""

    def __init__(self, cache_dir: Optional[Path] = None):
        super().__init__()
        self.cache_dir = cache_dir or Path(tempfile.mkdtemp(prefix="mcqpy_cache_"))
        self.cache_dir.mkdir(exist_ok=True, parents=True)

    def can_handle(self, url: str) -> bool:
        """Check if URL is a GitHub repository directory"""
        parsed = urlparse(url)
        return parsed.netloc == "github.com" and (
            "/tree/" in url or "/blob/" in url or url.endswith("/")
        )

    def load_quiz(self, url: str) -> Optional[Dict]:
        """Load quiz files from GitHub and cache everything locally"""
        try:
            # Convert GitHub URL to raw base URL
            raw_base_url = self._github_url_to_raw_base(url)
            if not raw_base_url:
                return None

            # Create subdirectories for this quiz
            quiz_cache_dir = self.cache_dir / "questions"
            quiz_cache_dir.mkdir(exist_ok=True)

            # Try to load config.yaml directly and cache it
            config_data = None
            config_url = f"{raw_base_url}/config.yaml"
            try:
                config_response = self.session.get(config_url)
                if config_response.status_code == 200:
                    config_data = yaml.safe_load(config_response.text)
                    # Cache config file
                    config_path = self.cache_dir / "config.yaml"
                    with open(config_path, "w") as f:
                        yaml.dump(config_data, f)
            except Exception:
                pass  # Config is optional

            # Load questions and download images
            questions = self._fetch_and_cache_questions(
                f"{raw_base_url}/questions", quiz_cache_dir
            )

            return {
                "config": config_data,
                "questions": questions,
                "source_url": url,
                "cache_dir": str(
                    self.cache_dir
                ),  # Include cache location for reference
                "loader_type": "cached",
            }
        except Exception as e:
            raise e

    def _fetch_and_cache_questions(
        self, base_raw_url: str, cache_dir: Path
    ) -> Dict[str, Dict]:
        """Fetch questions and download all referenced images locally"""
        questions = {}

        # Common question file patterns to try
        patterns = [
            # Pattern 1: question_001.yaml, question_002.yaml, etc.
            ["question_{:03d}.yaml".format(i) for i in range(1, 101)],
            # Pattern 2: question_1.yaml, question_2.yaml, etc.
            ["question_{}.yaml".format(i) for i in range(1, 51)],
            # Pattern 3: exam_2024_question_1.yaml, etc.
            ["exam_2024_question_{}.yaml".format(i) for i in range(1, 51)],
        ]

        downloaded_images = {}  # Track downloaded images to avoid duplicates

        # Try each pattern
        for pattern_set in patterns:
            for filename in pattern_set:
                question_url = f"{base_raw_url}/{filename}"
                try:
                    response = self.session.get(question_url)
                    if response.status_code == 200:
                        question_data = yaml.safe_load(response.text)
                        if question_data:  # Valid YAML
                            # Download images referenced in this question
                            self._download_and_replace_images(
                                question_data,
                                base_raw_url,
                                cache_dir,
                                downloaded_images,
                            )

                            # Cache the question file locally
                            question_path = cache_dir / filename
                            with open(question_path, "w") as f:
                                yaml.dump(question_data, f)

                            questions[filename] = question_data
                except Exception:
                    continue  # File doesn't exist or invalid, try next

            # If we found questions with this pattern, don't try other patterns
            if questions:
                break

        return questions

    def _download_and_replace_images(
        self,
        question_data: Dict,
        base_raw_url: str,
        cache_dir: Path,
        downloaded_images: Dict[str, str],
    ) -> None:
        """Download images and replace paths with local file paths"""
        image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".svg"]

        def download_and_replace(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "image" and isinstance(value, (list, str)):
                        # Handle image field specifically
                        if isinstance(value, str) and any(
                            value.endswith(ext) for ext in image_extensions
                        ):
                            local_path = self._download_image(
                                value, base_raw_url, cache_dir, downloaded_images
                            )
                            if local_path:
                                data[key] = str(local_path)
                        elif isinstance(value, list):
                            for i, img_path in enumerate(value):
                                if isinstance(img_path, str) and any(
                                    img_path.endswith(ext) for ext in image_extensions
                                ):
                                    local_path = self._download_image(
                                        img_path,
                                        base_raw_url,
                                        cache_dir,
                                        downloaded_images,
                                    )
                                    if local_path:
                                        value[i] = str(local_path)
                    else:
                        download_and_replace(value)
            elif isinstance(data, list):
                for item in data:
                    download_and_replace(item)

        download_and_replace(question_data)

    def _download_image(
        self,
        img_filename: str,
        base_raw_url: str,
        cache_dir: Path,
        downloaded_images: Dict[str, str],
    ) -> Optional[Path]:
        """Download a single image and return local path"""
        # Check if already downloaded
        if img_filename in downloaded_images:
            return Path(downloaded_images[img_filename])

        try:
            img_url = f"{base_raw_url.rstrip('/')}/{img_filename}"
            response = self.session.get(img_url)

            if response.status_code == 200:
                # Save image to cache directory
                img_path = cache_dir / img_filename
                img_path.write_bytes(response.content)

                # Track downloaded image
                downloaded_images[img_filename] = str(img_path)
                return img_path
        except Exception:
            pass

        return None

    def _github_url_to_raw_base(self, url: str) -> Optional[str]:
        """Convert GitHub URL directly to raw base URL"""
        try:
            # Parse different GitHub URL formats
            if "/tree/" in url:
                parts = url.split("/tree/")
                repo_part = parts[0].replace("https://github.com/", "")
                branch_and_path = parts[1].split("/", 1)
                branch = branch_and_path[0]
                path = branch_and_path[1] if len(branch_and_path) > 1 else ""
            elif "/blob/" in url:
                # Single file URL - get parent directory
                parts = url.split("/blob/")
                repo_part = parts[0].replace("https://github.com/", "")
                branch_and_path = parts[1].split("/", 1)
                branch = branch_and_path[0]
                path = (
                    str(Path(branch_and_path[1]).parent)
                    if len(branch_and_path) > 1
                    else ""
                )
            else:
                # Repository root
                repo_part = url.replace("https://github.com/", "").rstrip("/")
                branch = "main"  # Default branch
                path = ""

            # Build raw URL base
            raw_base = f"https://raw.githubusercontent.com/{repo_part}/{branch}"
            if path:
                raw_base += f"/{path}"

            return raw_base
        except Exception:
            return None

    def cleanup(self):
        """Clean up the temporary cache directory"""

        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
