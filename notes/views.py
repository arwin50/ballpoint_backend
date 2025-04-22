from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import NoteDocument, Category
from rest_framework import generics
from .serializers import NoteDocumentSerializer, CategorySerializer
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.response import Response
from rest_framework import status

class CategoryCreateView(APIView):
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoryUpdateView(UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'

class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
class CategoryDeleteView(DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'

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

