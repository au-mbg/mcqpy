from .base_loader import RemoteLoader
from .archive_loader import ArchiveLoader
from .github_loader import GitHubLoader
from .github_cache_loader import CachedGitHubLoader

loaders = [ArchiveLoader, GitHubLoader]
cached_loaders = [ArchiveLoader, CachedGitHubLoader]

from .dispatcher import RemoteQuizDispatcher, load_remote_quiz
