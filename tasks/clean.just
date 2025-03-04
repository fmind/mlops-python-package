# run clean tasks
[group('clean')]
clean: clean-build clean-cache clean-constraints clean-coverage clean-docs clean-environment clean-mlruns clean-mypy clean-outputs clean-pytest clean-python clean-requirements clean-ruff

# clean build folders
[group('clean')]
clean-build:
    rm -rf dist/
    rm -rf build/

# clean cache folder
[group('clean')]
clean-cache:
    rm -rf .cache/

# clean constraints file
[group('clean')]
clean-constraints:
    rm -rf constraints.txt

# clean coverage files
[group('clean')]
clean-coverage:
    rm -rf .coverage*

# clean docs folder
[group('clean')]
clean-docs:
    rm -rf docs/

# clean environment file
[group('clean')]
clean-environment:
    rm -f python_env.yaml

# clean mlruns folder
[group('clean')]
clean-mlruns:
    rm -rf mlruns/*

# clean mypy folders
[group('clean')]
clean-mypy:
    rm -rf .mypy_cache/

# clean outputs folder
[group('clean')]
clean-outputs:
    rm -rf outputs/*

# clean pytest cache
[group('clean')]
clean-pytest:
    rm -rf .pytest_cache/

# clean python caches
[group('clean')]
clean-python:
    find . -type f -name '*.py[co]' -delete
    find . -type d -name __pycache__ -exec rm -r {} \+

# clean requirements file
[group('clean')]
clean-requirements:
    rm -f requirements.txt

# clean ruff cache
[group('clean')]
clean-ruff:
    rm -rf .ruff_cache/

# clean venv folder
[confirm]
[group('clean')]
clean-venv:
    rm -rf .venv/
