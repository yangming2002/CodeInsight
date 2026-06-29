from core.parser import parse_changed_files
from core.policy import PolicyEngine


def review_diff(diff: str, repository: str | None = None, pr_number: int | None = None) -> dict[str, object]:
    findings = PolicyEngine().review(diff)
    finding_dicts = [finding.to_dict() for finding in findings]
    changed_files = [file.to_dict() for file in parse_changed_files(diff)]

    if finding_dicts:
        summary = f"Policy review found {len(finding_dicts)} issue(s) in the submitted diff."
    else:
        summary = "Policy review completed with no issues found in the submitted diff."

    return {
        "repository": repository,
        "pr_number": pr_number,
        "summary": summary,
        "changed_files": changed_files,
        "changed_file_count": len(changed_files),
        "findings": finding_dicts,
        "finding_count": len(finding_dicts),
        "llm_summary": "LLM reasoning is not enabled in MVP v0.",
    }
