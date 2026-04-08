from celery import shared_task

from .redis_client import set_cache
from .scanner import scan_folder


@shared_task(bind=True)
def scan_folder_task(self, path):
    tracks = scan_folder(path)

    cache_key = f"scan:{path}"
    set_cache(cache_key, tracks)

    from .scanner import group_by_genre
    grouped = group_by_genre(tracks)

    return {
        "status": "done",
        "grouped": grouped
    }