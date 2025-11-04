from pathlib import Path
from typing import Dict, Optional


from mcqpy.web.utils.remote_loader import cached_loaders, loaders


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
            self.loaders = [loader() for loader in cached_loaders]
        else:
            self.loaders = [loader() for loader in loaders]

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
def load_remote_quiz(
    url: str, use_cache: bool = False, cache_dir: Optional[Path] = None
) -> Optional[Dict]:
    from mcqpy.question import Question

    """Cached function to load remote quiz"""
    dispatcher = RemoteQuizDispatcher(use_cache=use_cache, cache_dir=cache_dir)
    contents = dispatcher.load_quiz_from_url(url)

    if contents is None:
        return None

    questions = contents.get("questions", {})
    config = contents.get("config", {})

    question_list = []

    # For archives, images are in the questions subdirectory of the cache
    if "cache_dir" in contents:
        cache_dir = Path(contents["cache_dir"])
        # Check if there's a questions subdirectory (typical for archives)
        questions_subdir = cache_dir / "questions"
        base_dir = questions_subdir if questions_subdir.exists() else cache_dir
    else:
        base_dir = Path("/nonexistent")
        
    context = {
        "base_dir": base_dir
    }

    for file, qdata in questions.items():
        # Note: Image paths should already be replaced with full URLs by the loaders
        # We pass a dummy context since images should now be URLs, not local paths
        question = Question.model_validate(qdata, context=context)
        question_list.append(question)

    return {"questions": question_list, "config": config}

if __name__ == "__main__":
    test_url = "https://github.com/au-mbg/mcqpy/blob/main/web_quiz/test_quiz.tar.gz"

    data = load_remote_quiz(test_url)
    
    if data:
        print(f"Successfully loaded {len(data['questions'])} questions")
        # Check one question with images
        for question in data['questions']:
            if hasattr(question, 'image') and question.image:
                print(f"Question '{question.slug}' has {len(question.image)} images")
                break
    else:
        print("Failed to load quiz")
