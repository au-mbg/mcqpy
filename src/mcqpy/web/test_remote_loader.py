#!/usr/bin/env python3
"""
Test script for the remote quiz loader functionality
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import mcqpy
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcqpy.web.utils.remote_loader import RemoteQuizLoader


def test_github_url_parsing():
    """Test GitHub URL parsing functionality"""
    loader = RemoteQuizLoader()
    
    test_urls = [
        "https://github.com/user/repo/tree/main/test_quiz",
        "https://github.com/user/repo/tree/main/local_tests/test_quiz",
        "https://github.com/user/repo",
    ]
    
    print("Testing GitHub URL parsing:")
    for url in test_urls:
        api_url = loader._github_url_to_api(url)
        print(f"  {url}")
        print(f"    -> {api_url}")
        print()


def test_url_detection():
    """Test URL type detection"""
    loader = RemoteQuizLoader()
    
    test_urls = [
        "https://github.com/user/repo/tree/main/test_quiz",
        "https://example.com/quiz.zip",
        "https://github.com/user/repo/archive/refs/heads/main.zip",
        "https://invalid-url.com/something",
    ]
    
    print("Testing URL type detection:")
    for url in test_urls:
        is_github = loader._is_github_repo_url(url)
        is_archive = url.endswith(('.zip', '.tar.gz'))
        print(f"  {url}")
        print(f"    GitHub: {is_github}, Archive: {is_archive}")
        print()


if __name__ == "__main__":
    print("MCQPy Remote Quiz Loader Test")
    print("=" * 40)
    print()
    
    test_url_detection()
    test_github_url_parsing()
    
    print("Test completed!")
    print()
    print("To test with a real URL, you can run:")
    print("python -c \"from mcqpy.web.utils.remote_loader import load_remote_quiz; print(load_remote_quiz('YOUR_URL_HERE'))\"")