# run install tasks
[group('install')]
install: install-project install-hooks

# install git hooks
[group('install')]
install-hooks:
    uv run pre-commit install --hook-type=pre-push
    uv run pre-commit install --hook-type=commit-msg

# install the project
[group('install')]
install-project:
    uv sync --all-groups

# install github rulesets
[group('install')]
install-rulesets:
    #!/usr/bin/env bash
    set -euo pipefail
    repo=$(gh repo view --json=name --jq=.name)
    owner=$(gh repo view --json=owner --jq=.owner.login)
    gh api --method POST -H "Accept: application/vnd.github+json" \
    "/repos/$owner/$repo/rulesets" --input=".github/rulesets/main.json"
