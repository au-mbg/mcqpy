"""
Remote Quiz Loader

Handles loading quiz configurations and questions from remote sources
like GitHub repositories or zip archives.
"""

import tempfile
import zipfile
import re
import base64
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse
import requests
import streamlit as st
import yaml


class RemoteLoader(ABC):
    """Base class for loading quiz files from remote sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MCQPy-Web/1.0'
        })
    
    @abstractmethod
    def load_quiz(self, url: str) -> Optional[Dict]:
        """
        Load a complete quiz from a URL
        
        Args:
            url: URL to load quiz from
            
        Returns:
            Dictionary with config and questions, or None if failed
        """
        pass
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """
        Check if this loader can handle the given URL
        
        Args:
            url: URL to check
            
        Returns:
            True if this loader can handle the URL, False otherwise
        """
        pass

class GitHubLoader(RemoteLoader):
    """Loader for GitHub repositories"""
    
    def can_handle(self, url: str) -> bool:
        """Check if URL is a GitHub repository directory"""
        parsed = urlparse(url)
        return (parsed.netloc == 'github.com' and 
                ('/tree/' in url or '/blob/' in url or url.endswith('/')))
    
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
            questions = self._fetch_questions_from_raw_directory(f"{raw_base_url.rstrip('/')}/questions")
            
            return {
                'config': config_data,
                'questions': questions,
                'source_url': url
            }
        except Exception as e:
            # st.error(f"Failed to load quiz from GitHub: {str(e)}")
            raise e
    
    def _github_url_to_raw_base(self, url: str) -> Optional[str]:
        """Convert GitHub URL directly to raw base URL (bypasses API rate limits)"""
        try:
            # Parse different GitHub URL formats
            if '/tree/' in url:
                parts = url.split('/tree/')
                repo_part = parts[0].replace('https://github.com/', '')
                branch_and_path = parts[1].split('/', 1)
                branch = branch_and_path[0]
                path = branch_and_path[1] if len(branch_and_path) > 1 else ''
            elif '/blob/' in url:
                # Single file URL - get parent directory
                parts = url.split('/blob/')
                repo_part = parts[0].replace('https://github.com/', '')
                branch_and_path = parts[1].split('/', 1)
                branch = branch_and_path[0]
                path = str(Path(branch_and_path[1]).parent) if len(branch_and_path) > 1 else ''
            else:
                # Repository root
                repo_part = url.replace('https://github.com/', '').rstrip('/')
                branch = 'main'  # Default branch
                path = ''
            
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
                            self._replace_image_paths_in_question_direct(question_data, base_raw_url)
                except Exception:
                    continue  # File doesn't exist or invalid, try next
                    
            # If we found questions with this pattern, don't try other patterns
            if questions:
                break
        
        return questions
    
    def _replace_image_paths_in_question_direct(self, question_data: Dict, base_raw_url: str) -> None:
        """Replace relative image paths with full GitHub raw URLs"""
        # Common image extensions to check for
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
        
        def replace_image_references(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'image' and isinstance(value, (list, str)):
                        # Handle image field specifically
                        if isinstance(value, str) and any(value.endswith(ext) for ext in image_extensions):
                            data[key] = f"{base_raw_url.rstrip('/')}/{value}"
                        elif isinstance(value, list):
                            for i, img_path in enumerate(value):
                                if isinstance(img_path, str) and any(img_path.endswith(ext) for ext in image_extensions):
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
            if 'api.github.com/repos/' not in api_url:
                return None
                
            # Remove API prefix and query parameters
            url_part = api_url.replace('https://api.github.com/repos/', '')
            if '?' in url_part:
                url_part, query = url_part.split('?', 1)
                # Extract branch from ref parameter
                branch = 'main'  # default
                for param in query.split('&'):
                    if param.startswith('ref='):
                        branch = param.split('=', 1)[1]
            else:
                branch = 'main'
            
            # Split into owner/repo and path
            parts = url_part.split('/')
            if len(parts) < 2:
                return None
                
            owner = parts[0] 
            repo = parts[1]
            path = '/'.join(parts[2:]) if len(parts) > 2 else ''
            
            # Build raw URL base
            raw_base = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}"
            if path:
                raw_base += f"/{path}"
            
            return raw_base
            
        except Exception:
            return None
    
    def _replace_image_paths_in_question(self, question_data: Dict, image_files: list, base_raw_url: str) -> None:
        """Replace relative image paths with full GitHub raw URLs in question data"""
        # Create mapping of image filenames to their full URLs
        image_map = {}
        for img_file in image_files:
            image_map[img_file['name']] = f"{base_raw_url}/{img_file['name']}"
        
        # Recursively process the question data to find and replace image references
        self._replace_images_recursive(question_data, image_map)
    
    def _replace_images_recursive(self, data, image_map: Dict[str, str]) -> None:
        """Recursively replace image paths in nested data structures"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'image' and isinstance(value, (list, str)):
                    # Handle image field specifically
                    if isinstance(value, str):
                        if value in image_map:
                            data[key] = image_map[value]
                    elif isinstance(value, list):
                        for i, img_path in enumerate(value):
                            if isinstance(img_path, str) and img_path in image_map:
                                value[i] = image_map[img_path]
                else:
                    # Recursively process other fields
                    self._replace_images_recursive(value, image_map)
        elif isinstance(data, list):
            for item in data:
                self._replace_images_recursive(item, image_map)
        elif isinstance(data, str):
            # Replace image references in string content (e.g., markdown)
            for img_name, img_url in image_map.items():
                # Replace markdown image syntax: ![alt](image.png) -> ![alt](full_url)  
                data = re.sub(rf'\!\[([^\]]*)\]\({re.escape(img_name)}\)', rf'![\1]({img_url})', data)
                # Replace HTML img tags: <img src="image.png"> -> <img src="full_url">
                data = re.sub(rf'src=["\']?{re.escape(img_name)}["\']?', f'src="{img_url}"', data)
            return data


class ArchiveLoader(RemoteLoader):
    """Loader for zip archives"""
    
    def can_handle(self, url: str) -> bool:
        """Check if URL is a zip archive"""
        return url.endswith(('.zip', '.tar.gz'))
    
    def load_quiz(self, url: str) -> Optional[Dict]:
        """Load quiz files from a zip archive"""
        try:
            # Download the archive
            response = self.session.get(url)
            response.raise_for_status()
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                archive_path = Path(temp_dir) / "archive.zip"
                archive_path.write_bytes(response.content)
                
                # Extract and find quiz files
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find config.yaml and questions directory
                config_data = None
                questions = {}
                
                for root, dirs, files in (Path(temp_dir)).walk():
                    if 'config.yaml' in files:
                        config_path = root / 'config.yaml'
                        with open(config_path, 'r') as f:
                            config_data = yaml.safe_load(f)
                    
                    if 'questions' in dirs:
                        questions_dir = root / 'questions'
                        questions = self._load_questions_from_local_dir(questions_dir)
                
                if config_data is None:
                    # st.error("No config.yaml found in the archive")
                    return None
                
                return {
                    'config': config_data,
                    'questions': questions,
                    'source_url': url
                }
        except Exception as e:
            # st.error(f"Failed to load quiz from archive: {str(e)}")
            raise e
    
    def _load_questions_from_local_dir(self, questions_dir: Path) -> Dict[str, Dict]:
        """Load question files from local directory and convert image paths to data URLs"""
        questions = {}
        
        try:
            # First, load all questions
            for yaml_file in questions_dir.glob('*.yaml'):
                with open(yaml_file, 'r') as f:
                    questions[yaml_file.name] = yaml.safe_load(f)
            
            # Find all image files in the same directory
            image_files = []
            for img_ext in ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg']:
                image_files.extend(questions_dir.glob(img_ext))
            
            # Create mapping of image filenames to data URLs
            image_map = {}
            for img_path in image_files:
                data_url = self._image_to_data_url(img_path)
                if data_url:
                    image_map[img_path.name] = data_url
            
            # Replace relative image paths with data URLs in all questions
            for question_file, question_data in questions.items():
                self._replace_images_recursive(question_data, image_map)
                
        except Exception:
            # st.error(f"Failed to load questions from directory")
            raise
        
        return questions
    
    def _image_to_data_url(self, img_path: Path) -> Optional[str]:
        """Convert local image file to data URL"""
        try:
            with open(img_path, 'rb') as f:
                img_data = f.read()
            
            # Determine MIME type based on extension
            ext = img_path.suffix.lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml'
            }
            
            mime_type = mime_types.get(ext, 'image/png')
            encoded_data = base64.b64encode(img_data).decode('utf-8')
            
            return f"data:{mime_type};base64,{encoded_data}"
            
        except Exception:
            return None
    
    def _replace_images_recursive(self, data, image_map: Dict[str, str]) -> None:
        """Recursively replace image paths in nested data structures"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'image' and isinstance(value, (list, str)):
                    # Handle image field specifically
                    if isinstance(value, str):
                        if value in image_map:
                            data[key] = image_map[value]
                    elif isinstance(value, list):
                        for i, img_path in enumerate(value):
                            if isinstance(img_path, str) and img_path in image_map:
                                value[i] = image_map[img_path]
                else:
                    # Recursively process other fields
                    self._replace_images_recursive(value, image_map)
        elif isinstance(data, list):
            for item in data:
                self._replace_images_recursive(item, image_map)
        elif isinstance(data, str):
            # Replace image references in string content (e.g., markdown)
            for img_name, img_url in image_map.items():
                # Replace markdown image syntax: ![alt](image.png) -> ![alt](data_url)
                data = re.sub(rf'\!\[([^\]]*)\]\({re.escape(img_name)}\)', rf'![\1]({img_url})', data)
                # Replace HTML img tags: <img src="image.png"> -> <img src="data_url">
                data = re.sub(rf'src=["\']?{re.escape(img_name)}["\']?', f'src="{img_url}"', data)


class CachedGitHubLoader(RemoteLoader):
    """GitHub loader that downloads questions and images to a temporary directory for local access"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        super().__init__()
        self.cache_dir = cache_dir or Path(tempfile.mkdtemp(prefix="mcqpy_cache_"))
        self.cache_dir.mkdir(exist_ok=True, parents=True)
    
    def can_handle(self, url: str) -> bool:
        """Check if URL is a GitHub repository directory"""
        parsed = urlparse(url)
        return (parsed.netloc == 'github.com' and 
                ('/tree/' in url or '/blob/' in url or url.endswith('/')))
    
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
                    with open(config_path, 'w') as f:
                        yaml.dump(config_data, f)
            except Exception:
                pass  # Config is optional
            
            # Load questions and download images
            questions = self._fetch_and_cache_questions(f"{raw_base_url}/questions", quiz_cache_dir)
            
            return {
                'config': config_data,
                'questions': questions,
                'source_url': url,
                'cache_dir': str(self.cache_dir),  # Include cache location for reference
                'loader_type': 'cached'
            }
        except Exception as e:
            raise e
    
    def _fetch_and_cache_questions(self, base_raw_url: str, cache_dir: Path) -> Dict[str, Dict]:
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
                                question_data, base_raw_url, cache_dir, downloaded_images
                            )
                            
                            # Cache the question file locally
                            question_path = cache_dir / filename
                            with open(question_path, 'w') as f:
                                yaml.dump(question_data, f)
                            
                            questions[filename] = question_data
                except Exception:
                    continue  # File doesn't exist or invalid, try next
                    
            # If we found questions with this pattern, don't try other patterns
            if questions:
                break
        
        return questions
    
    def _download_and_replace_images(self, question_data: Dict, base_raw_url: str, 
                                   cache_dir: Path, downloaded_images: Dict[str, str]) -> None:
        """Download images and replace paths with local file paths"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
        
        def download_and_replace(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'image' and isinstance(value, (list, str)):
                        # Handle image field specifically
                        if isinstance(value, str) and any(value.endswith(ext) for ext in image_extensions):
                            local_path = self._download_image(value, base_raw_url, cache_dir, downloaded_images)
                            if local_path:
                                data[key] = str(local_path)
                        elif isinstance(value, list):
                            for i, img_path in enumerate(value):
                                if isinstance(img_path, str) and any(img_path.endswith(ext) for ext in image_extensions):
                                    local_path = self._download_image(img_path, base_raw_url, cache_dir, downloaded_images)
                                    if local_path:
                                        value[i] = str(local_path)
                    else:
                        download_and_replace(value)
            elif isinstance(data, list):
                for item in data:
                    download_and_replace(item)
        
        download_and_replace(question_data)
    
    def _download_image(self, img_filename: str, base_raw_url: str, cache_dir: Path, 
                       downloaded_images: Dict[str, str]) -> Optional[Path]:
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
            if '/tree/' in url:
                parts = url.split('/tree/')
                repo_part = parts[0].replace('https://github.com/', '')
                branch_and_path = parts[1].split('/', 1)
                branch = branch_and_path[0]
                path = branch_and_path[1] if len(branch_and_path) > 1 else ''
            elif '/blob/' in url:
                # Single file URL - get parent directory
                parts = url.split('/blob/')
                repo_part = parts[0].replace('https://github.com/', '')
                branch_and_path = parts[1].split('/', 1)
                branch = branch_and_path[0]
                path = str(Path(branch_and_path[1]).parent) if len(branch_and_path) > 1 else ''
            else:
                # Repository root
                repo_part = url.replace('https://github.com/', '').rstrip('/')
                branch = 'main'  # Default branch
                path = ''
            
            # Build raw URL base
            raw_base = f"https://raw.githubusercontent.com/{repo_part}/{branch}"
            if path:
                raw_base += f"/{path}"
                
            return raw_base
        except Exception:
            return None
    
    def cleanup(self):
        """Clean up the temporary cache directory"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)


class RemoteQuizDispatcher:
    """Dispatcher that selects the appropriate loader for a given URL"""
    
    def __init__(self, use_cache=False, cache_dir=None):
        """
        Initialize dispatcher with loader options
        
        Args:
            use_cache: If True, use CachedGitHubLoader for GitHub URLs (downloads images locally)
            cache_dir: Optional custom cache directory for CachedGitHubLoader
        """
        if use_cache:
            self.loaders = [
                CachedGitHubLoader(cache_dir=cache_dir),
                ArchiveLoader()
            ]
        else:
            self.loaders = [
                GitHubLoader(),
                ArchiveLoader()
            ]
    
    def load_quiz_from_url(self, url: str) -> Optional[Dict]:
        """
        Load a complete quiz from a URL using the appropriate loader
        
        Args:
            url: URL to load quiz from
            
        Returns:
            Dictionary with config and questions, or None if failed
        """
        for loader in self.loaders:
            if loader.can_handle(url):
                return loader.load_quiz(url)
        
        # st.error("Unsupported URL format. Please provide a GitHub directory URL or zip archive.")
        return None


# @st.cache_data(ttl=300)  # Cache for 5 minutes
def load_remote_quiz(url: str, use_cache: bool = False, cache_dir: Optional[Path] = None) -> Optional[Dict]:
    from mcqpy.question import Question

    """Cached function to load remote quiz"""
    dispatcher = RemoteQuizDispatcher(use_cache=use_cache, cache_dir=cache_dir)
    contents = dispatcher.load_quiz_from_url(url)

    if contents is None:
        return None
    
    questions = contents.get('questions', {})
    config = contents.get('config', {})

    question_list = []

    context = {"base_dir": dispatcher.loaders[0].cache_dir if use_cache else Path("/nonexistent")}

    for file, qdata in questions.items():
        # Note: Image paths should already be replaced with full URLs by the loaders
        # We pass a dummy context since images should now be URLs, not local paths
        question = Question.model_validate(qdata, context=context)
        question_list.append(question)

    return {
        'questions': question_list,
        'config': config
    }


if __name__ == "__main__":
    # Example usage - test both approaches
    test_url = "https://github.com/au-mbg/mcqpy/tree/main/web_quiz/test_quiz/"
    
    print("=== Testing Regular GitHub Loader (Remote Images) ===")
    quiz_data_remote = load_remote_quiz(test_url, use_cache=False)
    
    if quiz_data_remote:
        print(f"Loaded {len(quiz_data_remote['questions'])} questions")
        for question in quiz_data_remote['questions']:
            if question.image:
                print(f"Question '{question.slug}' has remote images: {question.image}")
    else:
        print("Failed to load quiz data with remote loader")
    
    print("\n=== Testing Cached GitHub Loader (Local Images) ===")
    quiz_data_cached = load_remote_quiz(test_url, use_cache=True)
    
    if quiz_data_cached:
        print(f"Loaded {len(quiz_data_cached['questions'])} questions")
        print(f"Cache directory: {quiz_data_cached.get('cache_dir', 'Not specified')}")
        for question in quiz_data_cached['questions']:
            if question.image:
                print(f"Question '{question.slug}' has local images: {question.image}")
    else:
        print("Failed to load quiz data with cached loader")

