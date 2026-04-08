import os
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .redis_client import get_cache, set_cache
from .tasks import scan_folder_task
from celery.result import AsyncResult

from .scanner import group_by_genre, preview_by_genre, scan_folder


def get_valid_path_or_error(request):
    path = request.query_params.get("path")

    if not path:
        return None, Response(
            {"error": "path is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not os.path.exists(path):
        return None, Response(
            {"error": "invalid path"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return path, None

def get_cached_scan(path):
    try:
        cache_key = f"scan:{path}"
        cached = get_cache(cache_key)

        if cached:
            return cached

        tracks = scan_folder(path)
        set_cache(cache_key, tracks)

        return tracks

    except Exception as e:
        print("Redis error:", e)
        # fallback → no cache
        return scan_folder(path)

class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok"})


class ScanView(APIView):
    def get(self, request):
        path, error = get_valid_path_or_error(request)
        if error:
            return error

        task = scan_folder_task.delay(path)

        return Response({
            "task_id": task.id,
            "status": "started",
        })


class PreviewView(APIView):
    def get(self, request):
        path, error = get_valid_path_or_error(request)
        if error:
            return error

        tracks = get_cached_scan(path)
        preview = preview_by_genre(tracks)

        return Response({"preview": preview})

class TaskStatusView(APIView):
    def get(self, request, task_id):
        result = AsyncResult(task_id)

        return Response({
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None
        })
