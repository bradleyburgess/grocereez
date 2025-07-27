format:
	ruff format src/

check:
	ruff check src/

clean:
	cleanpy

test:
	.venv/bin/pytest

migrate:
	python manage.py migrate
