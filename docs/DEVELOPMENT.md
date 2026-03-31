# Development Setup Guide

This document provides instructions for setting up the Dividend Tracker development environment.

## Prerequisites

Before you begin, ensure you have the following installed:
- **macOS/Linux/Windows**: Node.js 16+ and npm
- **macOS**: `brew` package manager
- **Python**: 3.13+
- **Git**: Version control

## Install System Dependencies

### Redis

Redis is required for the Celery task queue system:

```bash
brew install redis
```

## Backend Setup

The backend is a Flask application with Celery for async task processing.

### 1. Create Python Virtual Environment

Navigate to the Python directory and create a virtual environment:

```bash
cd ./python
python -m venv ./venv
```

### 2. Activate Virtual Environment

**macOS/Linux:**
```bash
source ./venv/bin/activate
```

**Windows:**
```bash
./venv/Scripts/activate
```

### 3. Install Python Dependencies

```bash
make py-deps
```

Alternatively, you can install directly:
```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

From the `./python/src` directory, run the following migration commands:

```bash
cd ./python/src

# Initialize migrations directory
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration to database
flask db upgrade

# Seed database with initial data
flask seed-db
```

### 5. Start the Web Server

From the root directory:

```bash
make run-web
```

The Flask development server will start at `http://localhost:5000`

## Frontend Setup

The frontend is a React application written in TypeScript.

### 1. Install Frontend Dependencies

```bash
make ts-deps
```

Alternatively:
```bash
cd ./ts
npm install
```

### 2. Start the Development Server

From the root directory:

```bash
make run-fe
```

The React application will start at `http://localhost:3000`

## Redis and Celery Setup

Celery handles asynchronous tasks like syncing dividend data. It requires Redis as the message broker.

### 1. Start Redis

```bash
brew services start redis
```

To verify Redis is running:
```bash
redis-cli ping
```

You should see `PONG` as the response.

### 2. Start Celery Worker

Open a new terminal window and run:

```bash
make run-celery-worker
```

This will start the Celery worker that processes background tasks.

### 3. Start Celery Beat Scheduler

Open another terminal window and run:

```bash
make run-celery-beat
```

Celery Beat handles scheduled tasks (e.g., syncing dividend data every 5 minutes).

## Running Tests

### Python Tests

Run all Python tests:

```bash
make test-py
```

Run tests with coverage report:

```bash
make test-py-cov
```

## Available Make Commands

View all available make commands:

```bash
make help
```

Common commands:
- `make py-deps` - Install Python dependencies
- `make ts-deps` - Install frontend npm dependencies
- `make run-web` - Start Flask dev server
- `make run-fe` - Start React dev server
- `make run-celery-worker` - Start Celery worker
- `make run-celery-beat` - Start Celery scheduler
- `make test-py` - Run Python tests
- `make test-py-cov` - Run Python tests with coverage

## Project Structure

For details about the project architecture and structure, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## Troubleshooting

### Redis Connection Issues

If you get a connection error when running Celery, ensure Redis is running:
```bash
brew services start redis
```

### Database Errors

If you encounter database errors, reset the development database:
```bash
rm python/src/instance/dividends.db
cd python/src
flask db upgrade
flask seed-db
```

### Module Import Errors

Ensure you've activated the Python virtual environment:
```bash
source ./python/venv/bin/activate
```
