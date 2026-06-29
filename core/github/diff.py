from __future__ import annotations

from dataclasses import dataclass

import httpx


class GitHubDiffError(RuntimeError):
    pass


@dataclass(frozen=True)
class PullRequestDiff:
    repository: str
    pr_number: int
    diff: str
    source_url: str

    def to_dict(self) -> dict[str, object]:
        return {
            "repository": self.repository,
            "pr_number": self.pr_number,
            "diff": self.diff,
            "source_url": self.source_url,
        }


class GitHubDiffFetcher:
    def __init__(
        self,
        token: str | None = None,
        base_url: str = "https://api.github.com",
        timeout: float = 10.0,
        client: httpx.Client | None = None,
    ) -> None:
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = client

    def fetch_pull_request_diff(self, repository: str, pr_number: int) -> PullRequestDiff:
        normalized_repository = _normalize_repository(repository)
        if pr_number < 1:
            raise ValueError("pr_number must be greater than 0.")

        url = f"{self._base_url}/repos/{normalized_repository}/pulls/{pr_number}"
        headers = {
            "Accept": "application/vnd.github.v3.diff",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "CodeInsight",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        response = self._send(url=url, headers=headers)
        if response.status_code != 200:
            raise GitHubDiffError(
                f"GitHub diff fetch failed with status {response.status_code}: {response.text}"
            )

        return PullRequestDiff(
            repository=normalized_repository,
            pr_number=pr_number,
            diff=response.text,
            source_url=url,
        )

    def _send(self, url: str, headers: dict[str, str]) -> httpx.Response:
        if self._client:
            return self._client.get(url, headers=headers, timeout=self._timeout)

        with httpx.Client(timeout=self._timeout) as client:
            return client.get(url, headers=headers)


def _normalize_repository(repository: str) -> str:
    normalized = repository.strip().strip("/")
    parts = normalized.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("repository must use the 'owner/name' format.")
    return normalized
