from django.urls import path
from .views import extract_text,summarize_text, organize_text

urlpatterns = [
    path("extract-text", extract_text, name="extract_text"),
    path("summarize-text",summarize_text, name="summarize_text"),
    path("organize-text/", organize_text, name='organize_text'),

]
