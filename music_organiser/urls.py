from django.urls import path
from .views import HealthView, PreviewView, ScanView

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('scan/', ScanView.as_view(), name='scan'),
    path('preview/', PreviewView.as_view(), name='preview'),
]
