from django.urls import path

from .views import IngestAPIView, EmissionRecordListView, EmissionRecordReviewView

urlpatterns = [
    path('ingest/<str:source_type>/', IngestAPIView.as_view(), name='ingest'),
    path('records/', EmissionRecordListView.as_view(), name='emission-record-list'),
    path('records/<int:pk>/review/', EmissionRecordReviewView.as_view(), name='emission-record-review'),
]
