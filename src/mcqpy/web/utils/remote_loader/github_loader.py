"""
Remote Quiz Loader

Handles loading quiz configurations and questions from remote sources
like GitHub repositories or zip archives.
"""

from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

import yaml
from mcqpy.web.utils.remote_loader.base_loader import RemoteLoader

class GitHubLoader(RemoteLoader):
    """Loader for GitHub repositories"""

    def can_handle(self, url: str) -> bool:
        """Check if URL is a GitHub repository directory"""
        parsed = urlparse(url)
        return parsed.netloc == "github.com" and (
            "/tree/" in url or "/blob/" in url or url.endswith("/")
        )

    def load_quiz(self, url: str) -> Optional[Dict]:
        """Load quiz files from a GitHub directory using direct raw URLs (no API rate limits)"""
        try:
            # Convert GitHub URL to raw base URL
            raw_base_url = self._github_url_to_raw_base(url)
            if not raw_base_url:
                return None

            # Try to load config.yaml directly
            config_data = None
            config_url = f"{raw_base_url}/config.yaml"
            try:
                config_response = self.session.get(config_url)
                if config_response.status_code == 200:
                    config_data = yaml.safe_load(config_response.text)
            except Exception:
                pass  # Config is optional

            # Load questions from questions directory
            questions = self._fetch_questions_from_raw_directory(
                f"{raw_base_url.rstrip('/')}/questions"
            )

            return {"config": config_data, "questions": questions, "source_url": url}
        except Exception as e:
            # st.error(f"Failed to load quiz from GitHub: {str(e)}")
            raise e

    def _github_url_to_raw_base(self, url: str) -> Optional[str]:
        """Convert GitHub URL directly to raw base URL (bypasses API rate limits)"""
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

            # Build raw URL base - no API calls needed!
            raw_base = f"https://raw.githubusercontent.com/{repo_part}/{branch}"
            if path:
                raw_base += f"/{path}"

            return raw_base
        except Exception:
            return None

    def _fetch_yaml_content(self, download_url: str) -> Optional[Dict]:
        """Fetch and parse YAML content from URL"""
        try:
            response = self.session.get(download_url)
            response.raise_for_status()
            return yaml.safe_load(response.text)
        except Exception:
            # st.error(f"Failed to fetch YAML content")
            return None

    def _fetch_questions_from_raw_directory(self, base_raw_url: str) -> Dict[str, Dict]:
        """Fetch questions by trying common file patterns (no API calls needed)"""
        questions = {}

        # Common question file patterns to try
        patterns = [
            # Pattern 1: question_001.yaml, question_002.yaml, etc.
            ["question_{:03d}.yaml".format(i) for i in range(1, 101)],
            # Pattern 2: question_1.yaml, question_2.yaml, etc.
            ["question_{}.yaml".format(i) for i in range(1, 51)],
            # Pattern 3: exam_2024_question_1.yaml, etc. (your specific pattern)
            ["exam_2024_question_{}.yaml".format(i) for i in range(1, 51)],
        ]

        # Try each pattern
        for pattern_set in patterns:
            for filename in pattern_set:
                question_url = f"{base_raw_url}/{filename}"
                try:
                    response = self.session.get(question_url)
                    if response.status_code == 200:
                        question_data = yaml.safe_load(response.text)
                        if question_data:  # Valid YAML
                            questions[filename] = question_data
                            # Replace image paths in this question
                            self._replace_image_paths_in_question_direct(
                                question_data, base_raw_url
                            )
                except Exception:
                    continue  # File doesn't exist or invalid, try next

            # If we found questions with this pattern, don't try other patterns
            if questions:
                break

        return questions

    def _replace_image_paths_in_question_direct(
        self, question_data: Dict, base_raw_url: str
    ) -> None:
        """Replace relative image paths with full GitHub raw URLs"""
        # Common image extensions to check for
        image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".svg"]

        def replace_image_references(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "image" and isinstance(value, (list, str)):
                        # Handle image field specifically
                        if isinstance(value, str) and any(
                            value.endswith(ext) for ext in image_extensions
                        ):
                            data[key] = f"{base_raw_url.rstrip('/')}/{value}"
                        elif isinstance(value, list):
                            for i, img_path in enumerate(value):
                                if isinstance(img_path, str) and any(
                                    img_path.endswith(ext) for ext in image_extensions
                                ):
                                    value[i] = f"{base_raw_url.rstrip('/')}/{img_path}"
                    else:
                        replace_image_references(value)
            elif isinstance(data, list):
                for item in data:
                    replace_image_references(item)

        replace_image_references(question_data)

    def _api_url_to_raw_base(self, api_url: str) -> Optional[str]:
        """Convert GitHub API URL to raw file base URL"""
        try:
            # Example API URL: https://api.github.com/repos/owner/repo/contents/path?ref=branch
            # Convert to: https://raw.githubusercontent.com/owner/repo/branch/path/

            # Extract parts from API URL
            if "api.github.com/repos/" not in api_url:
                return None

            # Remove API prefix and query parameters
            url_part = api_url.replace("https://api.github.com/repos/", "")
            if "?" in url_part:
                url_part, query = url_part.split("?", 1)
                # Extract branch from ref parameter
                branch = "main"  # default
                for param in query.split("&"):
                    if param.startswith("ref="):
                        branch = param.split("=", 1)[1]
            else:
                branch = "main"

            # Split into owner/repo and path
            parts = url_part.split("/")
            if len(parts) < 2:
                return None

            owner = parts[0]
            repo = parts[1]
            path = "/".join(parts[2:]) if len(parts) > 2 else ""

            # Build raw URL base
            raw_base = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}"
            if path:
                raw_base += f"/{path}"

            return raw_base

        except Exception:
            return None

    def _replace_image_paths_in_question(
        self, question_data: Dict, image_files: list, base_raw_url: str
    ) -> None:
        """Replace relative image paths with full GitHub raw URLs in question data"""
        # Create mapping of image filenames to their full URLs
        image_map = {}
        for img_file in image_files:
            image_map[img_file["name"]] = f"{base_raw_url}/{img_file['name']}"

        # Recursively process the question data to find and replace image references
        self._replace_images_recursive(question_data, image_map)

    def _replace_images_recursive(self, data, cache_dir):
        """For ArchiveLoader, we don't convert images to data URLs - just return data as-is"""
        # Images will be accessible via file paths in the cache directory
        # No need to convert to data URLs for archive-based quizzes
        return data

