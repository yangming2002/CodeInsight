# Contributing

CodeInsight follows a simple company-style Pull Request workflow.

## Development Workflow

1. Start from the latest `master`.

```bash
git checkout master
git pull origin master
```

2. Create a focused feature branch.

```bash
git checkout -b feature/short-description
```

3. Make one focused change.

Good PR scope:

- one bug fix
- one endpoint
- one parser
- one policy rule group
- one documentation update

4. Review your own diff before committing.

```bash
git status
git diff
```

5. Run tests.

```bash
python -m pytest
```

6. Commit with a clear message.

```bash
git add <files>
git commit -m "feat: add focused capability"
```

Useful prefixes:

```text
feat: new feature
fix: bug fix
docs: documentation
test: tests
refactor: behavior-preserving restructuring
chore: maintenance
```

7. Push and open a PR.

```bash
git push origin feature/short-description
```

## PR Description Template

```markdown
## What changed
- 

## Why
- 

## How tested
- python -m pytest
```

## Engineering Rules

- Keep `master` stable.
- Do not commit `.venv`, `.idea`, logs, caches, generated files, or secrets.
- Keep API logic in `apps/api`.
- Keep GitHub integration in `core/github`.
- Keep deterministic review rules in `core/policy`.
- Keep parsing and repository structure logic in `core/parser`.
- Keep orchestration in `core/review`.
- Add or update tests with behavior changes.
- Update README completion markers when a capability is actually done.
