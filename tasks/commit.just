# bump package
[group('commit')]
commit-bump:
    uv run cz bump

# commit package
[group('commit')]
commit-files:
    uv run cz commit

# get commit info
[group('commit')]
commit-info:
    uv run cz info
