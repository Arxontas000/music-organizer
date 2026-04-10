from celery import shared_task
from .redis_client import set_cache
from .scanner import group_by_genre
import os
import time

@shared_task(bind=True)
def scan_folder_task(self, path):
    from .scanner import get_metadata, parse_filename, clean_text, normalize_artist, classify_genre

    all_files = []

    # ✅ single scan (collect files)
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.lower().endswith(('.mp3', '.wav', '.flac')):
                full_path = os.path.join(root, name)
                all_files.append(full_path)

    total_files = len(all_files)
    tracks = []

    # ✅ process files
    for idx, full_path in enumerate(all_files, start=1):
        metadata = get_metadata(full_path)

        if metadata["artist"] == "Unknown" and metadata["title"] == "Unknown":
            metadata = parse_filename(full_path)

        metadata["artist"] = clean_text(metadata["artist"])
        metadata["title"] = clean_text(metadata["title"])
        metadata["artist"] = normalize_artist(metadata["artist"])

        track = {
            "path": full_path,
            "artist": metadata["artist"],
            "title": metadata["title"],
        }

        track["genre"] = classify_genre(track)
        tracks.append(track)

        # ✅ progress update
        progress = int((idx / total_files) * 100)

        self.update_state(
            state="PROGRESS",
            meta={"progress": progress}
        )

        time.sleep(0.05)

    cache_key = f"scan:{path}"
    set_cache(cache_key, tracks)

    grouped = group_by_genre(tracks)

    return {
        "status": "done",
        "grouped": grouped
    }