check_dirs := tests src

quality:
	black --check $(check_dirs)
	ruff $(check_dirs)

style:
	black $(check_dirs)
	ruff $(check_dirs)

test:
	pytest -sv ./tests