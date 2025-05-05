from django.urls import path
from .views import extract_text, summarize_text, WhisperTranscribeView

urlpatterns = [
    path("extract-text", extract_text, name="extract_text"),
    path("summarize-text",summarize_text, name="summarize_text"),
    path("whisper-audio", WhisperTranscribeView.as_view(), name="whisper-transcribe"),
]
