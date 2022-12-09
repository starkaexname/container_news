from celery import shared_task
from .parser import update_news


@shared_task
def updating():
    update_news()
