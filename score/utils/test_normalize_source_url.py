import pytest

from .normalize_source_url import normalize_source_url


def test_normalize_source_url_git_ssh_syntax():
    """Test that git SSH syntax is converted to HTTPS URLs."""
    # GitHub SSH syntax
    assert (
        normalize_source_url("git@github.com:user/repo")
        == "https://github.com/user/repo"
    )
    assert (
        normalize_source_url("git@github.com:user/repo.git")
        == "https://github.com/user/repo"
    )

    # GitLab SSH syntax
    assert (
        normalize_source_url("git@gitlab.com:user/repo")
        == "https://gitlab.com/user/repo"
    )
    assert (
        normalize_source_url("git@gitlab.com:user/repo.git")
        == "https://gitlab.com/user/repo"
    )

    # Bitbucket SSH syntax
    assert (
        normalize_source_url("git@bitbucket.org:user/repo")
        == "https://bitbucket.org/user/repo"
    )
    assert (
        normalize_source_url("git@bitbucket.org:user/repo.git")
        == "https://bitbucket.org/user/repo"
    )


def test_normalize_source_url_https_urls():
    """Test that HTTPS URLs are normalized correctly."""
    # GitHub HTTPS URLs
    assert (
        normalize_source_url("https://github.com/user/repo")
        == "https://github.com/user/repo"
    )
    assert (
        normalize_source_url("https://github.com/user/repo.git")
        == "https://github.com/user/repo"
    )
    assert (
        normalize_source_url("https://github.com/user/repo/")
        == "https://github.com/user/repo"
    )

    # GitLab HTTPS URLs
    assert (
        normalize_source_url("https://gitlab.com/user/repo")
        == "https://gitlab.com/user/repo"
    )
    assert (
        normalize_source_url("https://gitlab.com/user/repo.git")
        == "https://gitlab.com/user/repo"
    )

    # Bitbucket HTTPS URLs
    assert (
        normalize_source_url("https://bitbucket.org/user/repo")
        == "https://bitbucket.org/user/repo"
    )
    assert (
        normalize_source_url("https://bitbucket.org/user/repo.git")
        == "https://bitbucket.org/user/repo"
    )


def test_normalize_source_url_edge_cases():
    """Test edge cases and invalid inputs."""
    # None input
    assert normalize_source_url(None) is None

    # Empty string
    assert normalize_source_url("") is None

    # Invalid GitHub URLs (not 2 components)
    assert normalize_source_url("https://github.com/user") is None
    assert normalize_source_url("https://github.com/user/repo/extra") is None

    # Non-standard hosts should pass through unchanged
    assert (
        normalize_source_url("https://example.com/user/repo")
        == "https://example.com/user/repo"
    )
    assert (
        normalize_source_url("git@example.com:user/repo")
        == "https://example.com/user/repo"
    )
