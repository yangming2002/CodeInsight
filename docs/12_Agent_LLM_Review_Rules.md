# Agent / LLM Review Rules

CodeInsight should not stop at generic checks such as secrets, debug prints, or TODO comments.

This document defines the first deterministic rules for Agent / LLM application review.

## Why These Rules Exist

Agent and LLM applications often fail in ways that normal linters do not understand:

- LLM requests may hang without timeout.
- Tool calls may execute unsafe shell commands.
- Model output may be parsed as trusted JSON without schema validation.

These problems are not always syntax errors. They are engineering reliability and safety risks.

## Current Rules

| Rule | Severity | What It Detects | Why It Matters |
| --- | --- | --- | --- |
| `LLM001` | high | LLM API calls without explicit timeout | Prevents requests from hanging and blocking workers |
| `LLM002` | medium | `json.loads(...)` on likely model output | Prevents trusting unvalidated model output |
| `AGT001` | critical | `shell=True` in added code | Reduces command injection and unsafe tool execution risk |

## Examples

### LLM001

Risky:

```python
response = client.responses.create(model="gpt-5", input=prompt)
```

Preferred:

```python
response = client.responses.create(model="gpt-5", input=prompt, timeout=30)
```

### LLM002

Risky:

```python
payload = json.loads(response.output_text)
```

Preferred:

```python
payload = ReviewSchema.model_validate_json(response.output_text)
```

### AGT001

Risky:

```python
subprocess.run(command, shell=True)
```

Preferred:

```python
subprocess.run(["git", "status"], check=True, timeout=10)
```

## Current Limitations

These rules are intentionally simple. They inspect added diff lines and do not yet perform full AST or data-flow analysis.

Known limitations:

- Multi-line LLM calls may not be fully understood.
- A line containing `timeout` may still have weak error handling.
- Schema validation is detected by convention, not by full type analysis.
- `shell=True` is always flagged, even in tests.

This is acceptable for MVP because the goal is to establish the review pipeline and rule taxonomy before adding deeper AST/context analysis.

## Next Improvements

- Add AST-aware checks for multi-line calls.
- Detect retry and fallback policies around LLM calls.
- Detect structured output schemas for LLM reviewers.
- Distinguish production code from tests.
- Attach repository context to each finding.
