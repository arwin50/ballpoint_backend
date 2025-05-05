from django.urls import path
from .views import extract_text

urlpatterns = [
    path("extract-text", extract_text, name="extract_text"),
]