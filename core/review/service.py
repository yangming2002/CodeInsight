from pathlib import Path

from core.context import ReviewContextBuilder
from core.parser import RepositoryStructureParser, parse_changed_files
from core.policy import PolicyEngine


def review_diff(
    diff: str,
    repository: str | None = None,
    pr_number: int | None = None,
    repository_root: str | Path | None = None,
) -> dict[str, object]:
    findings = PolicyEngine().review(diff)
    changed_files = parse_changed_files(diff)
    snapshot = RepositoryStructureParser().parse(repository_root or Path.cwd())
    context = ReviewContextBuilder().build(changed_files=changed_files, snapshot=snapshot)
    finding_dicts = []
    for finding in findings:
        finding_dict = finding.to_dict()
        finding_dict["context"] = context.for_file(finding.file).to_dict()
        finding_dicts.append(finding_dict)
    changed_file_dicts = [file.to_dict() for file in changed_files]

    if finding_dicts:
        summary = f"Policy review found {len(finding_dicts)} issue(s) in the submitted diff."
    else:
        summary = "Policy review completed with no issues found in the submitted diff."

    return {
        "repository": repository,
        "pr_number": pr_number,
        "summary": summary,
        "changed_files": changed_file_dicts,
        "changed_file_count": len(changed_file_dicts),
        "context": context.to_dict(),
        "findings": finding_dicts,
        "finding_count": len(finding_dicts),
        "llm_summary": "LLM reasoning is not enabled in MVP v0.",
    }
