# Getting Started

This project is a mono-repo consisting of a Python Backend and a React Frontend in Typescript

## Install Necessary Packages
```
brew install redis
````

## To Initialise the Backend

1. Create Python virtual Envionment with the `python` directory
   - `cd ./python`
   - `python -m venv ./venv`

1. Activate the Python Virtual Environment
   - Windows `./python./venv/Scripts/activate`
   - MacOS `source ./python/.venv/bin/activate`
2. Install dependencies
   - Run `make py-deps`
3. Initialise the Webserver
   - Run `make run-web`
4. Open a new terminal window 
   - Navigate to `./python/src`
   - Run 
      ```bash
      flask db init
      flask db migrate -m "Initial migration"
      flask db upgrade
      ```

## To Initialise the Frontend

1. Install depedencies
   - Run `make ts-deps`
2. Start the development server
   - Run `make run-fe`

## To Initialise Redis and Celery

1. Ensure Redis is running
   - `brew services start redis`
   - Run `make run-celery-worker`
   - Run `make run-celery-beat`
