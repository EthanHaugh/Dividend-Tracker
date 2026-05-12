# Architecture Overview

Dividend Tracker is a full-stack dividend portfolio management application built as a monorepo with separate backend and frontend components.

## Project Structure

```
Dividend-Tracker/
├── python/                  # Backend (Flask + Celery)
│   └── src/
│       ├── app/            # Flask application configuration
│       ├── routes/         # API endpoints
│       ├── database/       # SQLAlchemy models and database setup
│       ├── celery_service/ # Celery tasks and scheduling
│       ├── models/         # Business logic models
│       ├── consts/         # Application constants
│       ├── utils/          # Utility functions
│       ├── migrations/     # Alembic database migrations
│       └── tests/          # Python unit tests
│
├── ts/                     # Frontend (React + TypeScript)
│   └── src/
│       ├── components/     # Reusable React components
│       ├── hooks/          # Custom React hooks
│       └── models/         # TypeScript interfaces
│
├── docs/                   # Documentation
├── makefile                # Development commands
├── requirements.txt        # Python dependencies
└── pyproject.toml          # Python project configuration
```

## Technology Stack

### Backend
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (development), Alembic for migrations
- **Task Queue**: Celery with Redis broker
- **API**: RESTful JSON API
- **Testing**: pytest with coverage
- **Type Checking**: mypy with SQLAlchemy plugin
- **Python Version**: 3.13+

### Frontend
- **Framework**: React 19
- **Language**: TypeScript 4.9+
- **UI Libraries**: Ant Design (antd), Material-UI Charts (@mui/x-charts)
- **Styling**: CSS Modules, Emotion
- **Build Tool**: Create React App (react-scripts)
- **Testing**: Jest + React Testing Library
- **Charts**: Chart.js via react-chartjs-2

### Infrastructure
- **Message Broker**: Redis
- **Async Tasks**: Celery
- **Scheduling**: Celery Beat

## Architecture Patterns

### Backend Architecture

#### API Layer (`routes/`)
- RESTful endpoints for dividend data
- Query validation and error handling
- Endpoints for:
  - Open positions
  - Yearly dividends
  - Dividend history
  - Account metadata

#### Business Logic (`models/`)
- Business entity classes
- Domain logic independent of frameworks
- Data transformation and calculations

#### Database Layer (`database/`)
- SQLAlchemy models representing domain entities
- Database initialization and configuration
- Model serialization methods (`.asdict()`)

#### Celery Service (`celery_service/`)
- **Tasks** (`tasks/sync_tasks.py`): Background jobs for syncing data
  - Sync positions (every 5 minutes)
  - Sync account summary (every 5 minutes)
  - Sync dividend history (monthly)
- **Services** (`services/sync_service.py`): Integration with external data sources
- **Utilities** (`services/utils.py`): Helper functions for syncing

#### Configuration (`app/config.py`)
- Environment-specific settings
- Celery beat schedule configuration
- Database connection settings
- Feature flags

### Frontend Architecture

#### Component Organization
- **Presentational Components**: Reusable UI components (dividends table, charts, cards)
- **Page Components**: Full page layouts
- **Hooks** (`hooks/`): Custom React hooks for API calls and shared logic

#### State Management
- React hooks (`useState`, `useEffect`)
- Custom API hook for backend communication
- Component-level state

#### Styling
- CSS Modules for component-scoped styles
- Emotion for styled components
- Global styles in `styles/styles.css`

### Data Flow

```
User Interaction (React)
        ↓
API Hooks (api.hooks.ts)
        ↓
Flask REST API (routes/endpoints.py)
        ↓
SQLAlchemy Models + Database
        ↓
Celery Tasks (background sync)
        ↓
External Data Sources
```

## Key Features

### Dividend Portfolio Tracking
- Track dividend-paying stocks
- View dividend history
- Monitor positions
- Calculate yearly dividend totals

### Automated Data Sync
- Celery Beat scheduler runs periodic sync tasks
- Updates positions every 5 minutes
- Updates account summary every 5 minutes
- Updates dividend history monthly

### Dashboard Visualization
- Line charts for dividend trends
- Pie charts for portfolio distribution
- Data tables with sorting and filtering
- Summary cards with key metrics

## Database Schema

Key entities tracked by SQLAlchemy models:

- **Company**: Dividend-paying companies in the portfolio
- **Dividend**: Individual dividend payments
- **YearlyDividends**: Aggregated dividend totals by year
- **AccountMetadata**: User account and portfolio information

## API Endpoints

Main endpoints provided by the backend:

- `GET /open-positions` - List current stock positions
- `GET /yearly-dividends` - Get yearly dividend totals (filterable by year)
- `GET /total-dividends` - Get total dividends across all time
- `GET /health` - Health check endpoint

See [DEVELOPMENT.md](./DEVELOPMENT.md) for setup instructions and testing details.

## Development Workflow

1. **Backend Development**: Python changes in `python/src/`
2. **Frontend Development**: React/TypeScript changes in `ts/src/`
3. **Database Changes**: Create migrations in `python/src/migrations/`
4. **Celery Tasks**: Add new tasks in `python/src/celery_service/tasks/`
5. **Testing**: Run `make test-py` for backend, `npm test` in `ts/` for frontend

## Performance Considerations

- **Caching**: Celery tasks cache frequently accessed data
- **Database Indexing**: SQLAlchemy models should be indexed on frequently queried fields
- **API Pagination**: Consider implementing pagination for large datasets
- **Frontend Optimization**: React components use CSS Modules for efficient styling

## Environment Variables

- **FLASK_ENV**: One of `PRODUCTION`, `DEVELOPMENT` or `TESTING`
- **REDIS_URL**: Broker URL to enable Celery scheduling
- **ALLOWED_ORIGINS**: CORS configuration, specify which origins can interact with the web server
- **DATABASE_URL**: The Database URL to point to in production, in development this defaults to SQLite

## Security Notes

- Database connections use SQLite for development (upgrade to PostgreSQL for production)
- Redis runs locally without authentication in development
- API endpoints should have CORS configuration reviewed for production
- Input validation on all API endpoints to prevent SQL injection
