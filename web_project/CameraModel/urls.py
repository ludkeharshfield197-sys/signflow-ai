from django.urls import path
from . import views

urlpatterns = [
    path('init/', views.CameraView.as_view(), name='camera_init'),
    path('export/', views.export_results, name='camera_export'),
    path('sessions/', views.camera_sessions, name='camera_sessions'),
    path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('clean-frames/', views.clean_frame_records, name='clean_frame_records'),
    # path('export-results/', views.export_results, name='export_results'),
    path('dome/', views.dome, name='dome'),
    path('sentence/', views.generate_sentence_from_detection, name='camera_sentence'),
] 