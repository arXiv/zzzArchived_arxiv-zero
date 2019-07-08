"""Provides a configured Celery application for async tasks."""

from celery import Celery

celery_app = Celery('zero')
celery_app.config_from_object('zero.celeryconfig')
celery_app.autodiscover_tasks(['zero'], related_name='tasks', force=True)
