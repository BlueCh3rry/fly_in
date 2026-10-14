.PHONY: install run debug clean lint lint-strict

E1 := easy/01_linear_path.txt
E2 := easy/02_simple_fork.txt
E3 := easy/03_basic_capacity.txt

M1 := medium/01_dead_end_trap.txt
M2 := medium/02_circular_loop.txt
M3 := medium/03_priority_puzzle.txt

H1 := hard/01_maze_nightmare.txt
H2 := hard/02_capacity_hell.txt
H3 := hard/03_ultimate_challenge.txt

C1 := challenger/01_the_impossible_dream.txt

FOLDER1 := /home/mmakhmae/42cursus/fly_in/maps
ARG := $(FOLDER1)/$(H1)

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
	uv run mypy *.py --strict
