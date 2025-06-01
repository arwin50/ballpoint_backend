from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework import status
from .serializers import CustomUserSerializer, RegisterSerializer, LoginSerializer, UpdateUsernameSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from google.auth.exceptions import GoogleAuthError
from dotenv import load_dotenv
import os

load_dotenv()

User = get_user_model()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_view(request):
    serializer = CustomUserSerializer(request.user)
    return Response(serializer.data)

@api_view(["POST"])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data  # User is returned from serializer
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Serialize user data
        user_serializer = CustomUserSerializer(user)

        return Response(
            {
                "access": access_token, 
                "refresh": str(refresh),
                "user": user_serializer.data
            }, 
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def logout_view(request):
    try:
        # Get refresh token from request data instead of cookies
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token

        # If user is authenticated, blacklist their tokens
        if hasattr(request, 'user') and request.user.is_authenticated:
            OutstandingToken.objects.filter(user=request.user).delete()

    except Exception as e:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

@api_view(["POST"])
def refresh_jwt(request):
    refresh_token = request.data.get("refresh")
    
    if not refresh_token:
        return Response(
            {"error": "Refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)
        return Response({"access": new_access_token})
    except TokenError as e:
        return Response(
            {"error": "Invalid or expired refresh token."},
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(["POST"])
def google_login_view(request):
    id_token_from_client = request.data.get('id_token')
    if not id_token_from_client:
        return Response({'error': 'ID token is required'}, status=status.HTTP_400_BAD_REQUEST)
 
    try:
        id_info = google_id_token.verify_oauth2_token(
            id_token_from_client,
            google_requests.Request(),
            os.getenv('GOOGLE_CLIENT_ID') 
        )
        

        email = id_info.get('email')
        first_name = id_info.get('given_name', '')
        last_name = id_info.get('family_name', '')
        username = email.split('@')[0]  # basic username

        if not email:
       
            return Response({'error': 'Google account did not return an email'}, status=status.HTTP_400_BAD_REQUEST)

        # Try to get existing user, or create if not exists
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                # Optionally: set is_active=True if you want immediate login
                'is_active': True,
            }
        )

        # You could update names if user was just created
        if created:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Serialize user data
        from .serializers import CustomUserSerializer
        user_serializer = CustomUserSerializer(user)
        
        print("access_token", access_token)

        return Response({
            "access": access_token,
            "refresh": str(refresh),
            "user": user_serializer.data
        }, status=status.HTTP_200_OK)

    except ValueError as ve:
        print("ValueError:", ve)
        return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)

    except GoogleAuthError as ge:
        print("GoogleAuthError:", ge)
        return Response({'error': str(ge)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        print("Unexpected error:", e)
        return Response({'error': 'Unexpected error: ' + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_username(request):
    serializer = UpdateUsernameSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user  # Get the authenticated user
        new_username = serializer.validated_data["username"]
        
        # Update the username
        user.username = new_username
        user.save()

        # Return the updated user data
        from .serializers import CustomUserSerializer
        user_serializer = CustomUserSerializer(user)
        return Response(user_serializer.data, status=200)

    return Response(serializer.errors, status=400)

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    user = request.user
    if 'photo' in request.FILES:
        user.profile_picture = request.FILES['photo']
        user.save()
        return Response({
            "profile_picture": user.profile_picture.url  # Cloudinary URL
        }, status=200)
    return Response({"error": "No photo uploaded."}, status=400)
