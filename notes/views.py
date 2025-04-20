from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import NoteDocument, Category
from rest_framework import generics
from .serializers import NoteDocumentSerializer, CategorySerializer
from django.db.models import Q
class NoteDocumentListCreate(generics.ListCreateAPIView):
    queryset = NoteDocument.objects.all()
    serializer_class = NoteDocumentSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(notesContent__icontains=search_query)
            )

        return queryset

class NoteDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = NoteDocument.objects.all()
    serializer_class = NoteDocumentSerializer


class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "label"
