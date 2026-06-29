from fastapi.testclient import TestClient

from apps.api.main import app


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
    assert body["finding_count"] == 3
    assert rule_ids == {"SEC001", "DBG001", "MTN001"}
