from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import NoteDocument
from rest_framework import generics
from .serializers import NoteDocumentSerializer

class NoteDocumentListCreate(generics.ListCreateAPIView):
    queryset = NoteDocument.objects.all()
    serializer_class = NoteDocumentSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)  # Allow form-data

class NoteDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NoteDocument.objects.all()
    serializer_class = NoteDocumentSerializer
