from celery import Celery

celery = Celery(__name__)
flask_app = None

def init_celery(app=None):
    global flask_app
    
    if app is None:
        from app import create_app
        app = create_app()
    
    flask_app = app
    
    celery.conf.update(app.config)
    celery.conf.broker_url = app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    celery.conf.result_backend = app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    celery.conf.beat_schedule = app.config.get('CELERY_BEAT_SCHEDULE', {})

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    from tasks import sync_tasks  # noqa: F401
    
    return celery

# Don't call init_celery() here!