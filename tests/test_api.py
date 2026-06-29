from fastapi.testclient import TestClient

from apps.api.main import app
from core.github import GitHubDiffError, PullRequestDiff


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "codeinsight-api"}


def test_review_returns_policy_findings() -> None:
    diff = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,2 +1,5 @@
 def main():
+    password = "super-secret-value"
+    print("debug")
+    # TODO: handle retries
     return True
"""

    response = client.post(
        "/review",
        json={"repository": "yangming2002/CodeInsight", "pr_number": 1, "diff": diff},
    )

    body = response.json()
    rule_ids = {finding["rule_id"] for finding in body["findings"]}

    assert response.status_code == 200
    assert body["repository"] == "yangming2002/CodeInsight"
    assert body["pr_number"] == 1
    assert body["changed_file_count"] == 1
    assert body["changed_files"][0]["path"] == "app.py"
    assert body["changed_files"][0]["added_lines"] == 3
    assert body["finding_count"] == 3
    assert rule_ids == {"SEC001", "DBG001", "MTN001"}


def test_pull_request_diff_endpoint(monkeypatch) -> None:
    class StubFetcher:
        def __init__(self, token=None):
            self.token = token

        def fetch_pull_request_diff(self, repository: str, pr_number: int) -> PullRequestDiff:
            return PullRequestDiff(
                repository=repository,
                pr_number=pr_number,
                diff="diff --git a/app.py b/app.py\n+print('debug')",
                source_url=f"https://api.github.com/repos/{repository}/pulls/{pr_number}",
            )

    monkeypatch.setattr("apps.api.main.GitHubDiffFetcher", StubFetcher)
    monkeypatch.setenv("GITHUB_TOKEN", "token-123")

    response = client.get("/github/pull-diff?repository=owner/repo&pr_number=3")

    body = response.json()

    assert response.status_code == 200
    assert body["repository"] == "owner/repo"
    assert body["pr_number"] == 3
    assert body["diff"].startswith("diff --git")


def test_pull_request_diff_endpoint_maps_fetch_error(monkeypatch) -> None:
    class StubFetcher:
        def __init__(self, token=None):
            self.token = token

        def fetch_pull_request_diff(self, repository: str, pr_number: int) -> PullRequestDiff:
            raise GitHubDiffError("GitHub diff fetch failed with status 404: not found")

    monkeypatch.setattr("apps.api.main.GitHubDiffFetcher", StubFetcher)

    response = client.get("/github/pull-diff?repository=owner/repo&pr_number=3")

    assert response.status_code == 502


def test_review_pull_request_endpoint_fetches_diff_and_reviews(monkeypatch) -> None:
    class StubFetcher:
        def __init__(self, token=None):
            self.token = token

        def fetch_pull_request_diff(self, repository: str, pr_number: int) -> PullRequestDiff:
            return PullRequestDiff(
                repository=repository,
                pr_number=pr_number,
                diff="""diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,1 +1,2 @@
+print("debug")
 return True
""",
                source_url=f"https://api.github.com/repos/{repository}/pulls/{pr_number}",
            )

    monkeypatch.setattr("apps.api.main.GitHubDiffFetcher", StubFetcher)

    response = client.get("/github/review-pr?repository=owner/repo&pr_number=3")
    body = response.json()

    assert response.status_code == 200
    assert body["repository"] == "owner/repo"
    assert body["pr_number"] == 3
    assert body["changed_file_count"] == 1
    assert body["finding_count"] == 1
    assert body["findings"][0]["rule_id"] == "DBG001"


def test_repository_structure_endpoint() -> None:
    response = client.get("/repository/structure")
    body = response.json()

    assert response.status_code == 200
    assert body["file_count"] > 0
    assert body["symbol_count"] > 0
    assert any(file["path"] == "apps/api/main.py" for file in body["files"])
    assert any(symbol["name"] == "health" for symbol in body["symbols"])
