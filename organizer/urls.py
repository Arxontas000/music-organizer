from django.urls import path
from .views import HealthView, PreviewView, ScanView, TaskStatusView

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('scan/', ScanView.as_view(), name='scan'),
    path('preview/', PreviewView.as_view(), name='preview'),

    path('task/<str:task_id>/', TaskStatusView.as_view(), name='task-status'),
]


