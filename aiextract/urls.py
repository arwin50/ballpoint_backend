from django.urls import path
from .views import extract_text,summarize_text

urlpatterns = [
    path("extract-text", extract_text, name="extract_text"),
    path("summarize-text",summarize_text, name="summarize_text")
]
