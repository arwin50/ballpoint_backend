from django.urls import path
from .views import *

urlpatterns = [
    path('', NoteDocumentListCreate.as_view(), name='note-list'),
    path('<int:pk>', NoteDocumentDetail.as_view(), name='note-detail'),
    path("categories/", CategoryListCreate.as_view(), name="category-list"),
    path("categories/<str:label>/", CategoryDetail.as_view(), name="category-detail"),
]
