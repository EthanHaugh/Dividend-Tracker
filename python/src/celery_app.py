from celery import Celery

celery = Celery(__name__)

def init_celery(app=None):
    if app is None:
        from app import create_app
        app = create_app()
    
    celery.conf.update(app.config)
    celery.conf.broker_url = app.config.get('CELERY_BROKER_URL')
    celery.conf.result_backend = app.config.get('CELERY_RESULT_BACKEND')

    celery.conf.beat_schedule = app.config.get('CELERY_BEAT_SCHEDULE', {})

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    from tasks import sync_tasks
    
    return celery

init_celery()