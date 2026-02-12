# Getting Started

This project is a mono-repo consisting of a Python Backend and a React Frontend in Typescript

To initialise the Bbackend:

1. Create Python virtual Envionment with the `python` directory
   - `cd ./python`
   - `python -m venv ./venv`

1. Activate the Python Virtual Environment
   - Windows `./python./venv/Scripts/activate`
   - MacOS `source ./python/.venv/bin/activate`
1. Once the Virtual Environment has initialised, install dependencies
   - Run `make py-deps`
1. Initialise the webserver
   - Run `make run-web`

To initialise the Frontend

1. Install depedencies
   - Run `make ts-deps`
2. Start the development server
   - Run `make run-fe`
