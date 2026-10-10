.PHONY: install run debug clean lint lint-strict

MAP := arg.txt
FOLDER1 := /home/mmakhmae/42cursus/fly_in/maps
FOLDER2 := C:/Users/Red/home/42Cursus/fly_in/arg.txt
ARG := $(FOLDER1)/$(MAP)

install:
	uv sync --python 3.11

run:
	uv run python3 main.py $(ARG)

debug:
	uv run python3 -m pdb main.py $(ARG)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -name .pytest_cache -exec rm -rf {} +
	find . -name .ruff_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete


lint:
	uv run flake8 *.py
	uv run mypy *.py\
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs \
		--exclude '(^\.venv/)'


lint-strict:
	uv run flake8 *.py
	uv run mypy *.py --exclude '(^\.venv/)'
