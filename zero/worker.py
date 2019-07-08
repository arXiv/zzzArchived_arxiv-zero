"""Entry-point for the Celery application."""

from .factory import create_worker_app, celery_app

app = create_worker_app()
# celery_app.conf.result_backend = 'file:///tmp/foo'
# celery_app.conf.broker_url = 'memory://localhost/'
app.app_context().push()