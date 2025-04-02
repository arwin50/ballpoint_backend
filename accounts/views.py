from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework import status
from .serializers import CustomUserSerializer, RegisterSerializer, LoginSerializer


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
        