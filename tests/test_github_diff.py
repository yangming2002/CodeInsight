import httpx
import pytest

from core.github import GitHubDiffError, GitHubDiffFetcher


def test_fetch_pull_request_diff_uses_github_diff_media_type() -> None:
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200, text="diff --git a/app.py b/app.py\n+print('debug')")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    fetcher = GitHubDiffFetcher(token="token-123", client=client)

    result = fetcher.fetch_pull_request_diff("owner/repo", 7)

    assert result.repository == "owner/repo"
    assert result.pr_number == 7
    assert result.diff.startswith("diff --git")
    assert result.source_url == "https://api.github.com/repos/owner/repo/pulls/7"
    assert captured_request is not None
    assert captured_request.headers["accept"] == "application/vnd.github.v3.diff"
    assert captured_request.headers["authorization"] == "Bearer token-123"
    assert captured_request.headers["user-agent"] == "CodeInsight"


def test_fetch_pull_request_diff_raises_on_github_error() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(404, text="not found"))
    )
    fetcher = GitHubDiffFetcher(client=client)

    with pytest.raises(GitHubDiffError, match="status 404"):
        fetcher.fetch_pull_request_diff("owner/repo", 7)


def test_fetch_pull_request_diff_validates_repository() -> None:
    fetcher = GitHubDiffFetcher()

    with pytest.raises(ValueError, match="owner/name"):
        fetcher.fetch_pull_request_diff("invalid", 1)


def test_fetch_pull_request_diff_validates_pr_number() -> None:
    fetcher = GitHubDiffFetcher()

    with pytest.raises(ValueError, match="greater than 0"):
        fetcher.fetch_pull_request_diff("owner/repo", 0)
