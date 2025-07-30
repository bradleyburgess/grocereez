test:
	.venv/bin/pytest -n auto

format:
	.venv/bin/ruff format src/

check:
	.venv/bin/ruff check src/

fix:
	.venv/bin/ruff check src/ --fix

clean:
	.venv/bin/cleanpy src/

run:
	python manage.py runserver

migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations
