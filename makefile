freeze:
	pip freeze > requirements.txt

py-deps:
	pip install -r requirements.txt

run-web:
	flask --app ./python/src/run.py run --debug

run-celery-worker:
	cd ./python/src && celery -A celery_app.celery worker --loglevel=info

run-celery-beat:
	cd ./python/src && celery -A celery_app.celery beat --loglevel=info

run-fe:
	cd ./ts/ && npm run start

ts-deps:
	cd ./ts/ && npm install