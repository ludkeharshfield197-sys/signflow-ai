from django.urls import path
from . import views

urlpatterns = [
    path('list', views.ModelListView.as_view(), name='model_list'),
    path('upload', views.ModelUploadView.as_view(), name='model_upload'),
    path('action', views.ModelActionView.as_view(), name='model_action'),
    path('save', views.ModelActionView.as_view(), name='model_save'),
    path('status', views.ModelActionView.as_view(), name='model_status'),
    path('download', views.ModelDownloadView.as_view(), name='model_download'),
]

