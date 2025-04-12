from django.urls import path
from .views import NoteDocumentListCreate, NoteDocumentDetail

urlpatterns = [
    path('', NoteDocumentListCreate.as_view(), name='note-list'),
    path('<str:pk>/', NoteDocumentDetail.as_view(), name='note-detail'),
]
