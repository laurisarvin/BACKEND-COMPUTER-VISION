from django.urls import path
from .views import DiagnosePlantView, DiagnosisHistoryView

urlpatterns = [
    path('diagnose/', DiagnosePlantView.as_view(), name='diagnose'),
    path('history/', DiagnosisHistoryView.as_view(), name='history'),
]