from django.urls import path
from . import views

app_name = 'agent'

urlpatterns = [
    path('knowledge-base/', views.knowledge_base_view, name='knowledge_base'),
    path('api/query/', views.query_knowledge_base, name='query_knowledge_base'),
    path('api/document/', views.document_handler, name='document_handler'),
    path('api/document/<int:doc_id>/', views.delete_document, name='delete_document'),
    path('api/document/<int:doc_id>/update/', views.update_document, name='update_document'),
    path('api/status/ollama/', views.check_ollama_status, name='check_ollama_status'),
]