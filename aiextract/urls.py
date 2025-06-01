from django.urls import path
from .views import extract_text, summarize_text,organize_text, query_text,complete_text, async_transcribe

urlpatterns = [
    path("extract-text", extract_text, name="extract_text"),
    path("summarize-text",summarize_text, name="summarize_text"),
    # path("whisper-audio", whisper_transcribe, name="whisper-transcribe"),
    path("organize-text", organize_text, name='organize_text'),
    path("complete-text",complete_text, name='autocomplete_text'),
    path("query-text",query_text,name="answer_query"),
    path("google-stt",async_transcribe,name="async-transcribe")
]
