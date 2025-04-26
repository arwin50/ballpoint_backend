from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import NoteDocument, Category
from rest_framework import generics
from .serializers import NoteDocumentSerializer, CategorySerializer, CategoryIDSerializer
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
    
class UpdateNoteCategoriesView(APIView):
    def put(self, request, id):
        try:
            # Fetch the NoteDocument by its ID
            note_document = NoteDocument.objects.get(noteID=id)

            # Wrap the categories list in a dictionary
            serializer = CategoryIDSerializer(data={"categories": request.data.get('categories', [])})
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Extract validated category IDs
            category_ids = serializer.validated_data['categories']

            # Fetch the Category instances corresponding to the IDs
            categories = Category.objects.filter(id__in=category_ids)

            # Check if all provided IDs are valid
            if len(categories) != len(category_ids):
                invalid_ids = set(category_ids) - set(categories.values_list('id', flat=True))
                return Response(
                    {"error": f"Invalid category IDs: {', '.join(invalid_ids)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update the categories of the NoteDocument
            note_document.categories.set(categories)

            return Response(
                {"message": "Categories updated successfully."},
                status=status.HTTP_200_OK
            )
        except NoteDocument.DoesNotExist:
            return Response(
                {"error": "NoteDocument not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

