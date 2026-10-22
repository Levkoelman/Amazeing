MAIN = a_maze_ing.py

CONFIG = config.txt

install:
	poetry install

run:
	poetry run python3 $(MAIN) $(CONFIG)

debug:
	poetry run python3 -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf dist

lint:
	poetry run flake8 .
	poetry run mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

.PHONY: install run debug clean lint
