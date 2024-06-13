runserver:
	docker compose up --build

tests:
	pytest --log-cli-level=INFO

format:
	black . && isort .

format_check:
	black --check . && isort --check-only .

quality_check:
	python -m pylint oper quiz && python -m mypy .


