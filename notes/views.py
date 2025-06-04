from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import NoteDocument, Category
from rest_framework import generics
from .serializers import NoteDocumentSerializer, CategorySerializer, CategoryIDSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.response import Response
from rest_framework import status

class CategoryCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoryUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class CategoryListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        categories = Category.objects.filter(user=request.user)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
class CategoryDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

class NoteDocumentListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NoteDocumentSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        user = self.request.user
        queryset = NoteDocument.objects.filter(user=user) 
        search_query = self.request.GET.get('search', '')

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(notesContent__icontains=search_query)
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  


class NoteDocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NoteDocumentSerializer

    def get_queryset(self):
        user = self.request.user
        return NoteDocument.objects.filter(user=user)  # Filter by the logged-in user
    
class UpdateNoteCategoriesView(APIView):
    def put(self, request, id):
        try:
            # Fetch the NoteDocument by its ID
            note_document = NoteDocument.objects.get(noteID=id)

            # Wrap the categories list in a dictionary
            serializer = CategoryIDSerializer(data={"categories": request.data.get('categories', [])})
            print("Request data:", request.data)  # Debugging line
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

    def get_queryset(self):
        user = self.request.user
        return NoteDocument.objects.filter(user=user) 

class CategoryListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    lookup_field = "id"

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
