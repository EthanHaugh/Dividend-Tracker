from app import create_app
from celery_service.celery_app import celery, init_celery
from celery.signals import worker_process_init

app = create_app()
init_celery(app)


@worker_process_init.connect
def init_worker(**kwargs):
    """Dispose of inherited DB connections after fork."""
    from database.db import db

    with app.app_context():
        db.engine.dispose()


if __name__ == "__main__":
    celery.start()
