format:
	.venv/bin/ruff format src/

check:
	.venv/bin/ruff check src/

fix:
	.venv/bin/ruff check src/ --fix

clean:
	.venv/bin/cleanpy src/

test:
	.venv/bin/pytest

migrate:
	python manage.py migrate
