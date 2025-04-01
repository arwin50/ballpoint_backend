from django.urls import path
from .views import NoteDocumentListCreate, NoteDocumentDetail

urlpatterns = [
    path('notes', NoteDocumentListCreate.as_view(), name='note-list'),
    path('notes/<int:pk>', NoteDocumentDetail.as_view(), name='note-detail'),
]
