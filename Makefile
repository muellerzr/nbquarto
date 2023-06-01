check_dirs := tests src

quality:
	black --check $(check_dirs)
	ruff $(check_dirs)

style:
	black $(check_dirs)
	ruff $(check_dirs) --fix

test:
	pytest -sv ./tests

documentation:
	nbquarto-process --config_file config.yaml --notebook_folder nbs/