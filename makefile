freeze:
	pip freeze > requirements.txt

dev:
	pip install -r requirements.txt

run:
	flask --app ./python/src/app.py run