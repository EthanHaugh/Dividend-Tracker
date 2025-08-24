freeze:
	pip freeze > requirements.txt

dev:
	pip install -r requirements.txt

run-web:
	flask --app ./python/src/app.py run --debug

run-fe:
	cd ./ts/ && npm run start
