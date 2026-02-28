import os

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    
    # Ensure instance directory exists
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'dividends.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = "redis://localhost:6379/0"

    CELERY_BEAT_SCHEDULE = {
        'sync-positions-onec-per-day': {
            'task': 'tasks.sync_tasks.sync_positions_task',
            'schedule': 86400 
        },
    }