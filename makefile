freeze:
	pip freeze > requirements.txt

py-deps:
	pip install -r requirements.txt

run-web:
	flask --app ./python/src/app.py run --debug

run-fe:
	cd ./ts/ && npm run start

ts-deps:
	cd ./ts/ && npm install