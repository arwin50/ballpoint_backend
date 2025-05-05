from django.urls import path
from .views import *

urlpatterns = [
    path('', NoteDocumentListCreate.as_view(), name='note-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='create-category'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/update/<str:id>/', CategoryUpdateView.as_view(), name='update-category'),
    path('categories/delete/<str:id>/', CategoryDeleteView.as_view(), name='delete-category'),
    path('<str:pk>/', NoteDocumentDetail.as_view(), name='note-detail'),
]
