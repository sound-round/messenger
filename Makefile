install:
	poetry install

force-package-install:
	pip install --force-reinstall --user dist/*.whl

package-install:
	pip install --user dist/*.whl

build:
	poetry build

publish:
	poetry publish --dry-run

#lint:
	#poetry run flake8 gendiff

test:
	poetry run pytest

test-coverage:
	#poetry run pytest --cov=gendiff --cov-report xml tests/
