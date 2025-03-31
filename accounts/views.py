from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
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

        response = Response(
            {"access": access_token, "refresh": str(refresh)}, 
            status=status.HTTP_200_OK
        )

        # Store refresh token in HTTP-only cookie (optional)
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax"
        )

        return response

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token

        # Optionally, blacklist all user's tokens (requires `rest_framework_simplejwt.token_blacklist`)
        OutstandingToken.objects.filter(user=request.user).delete()

    except Exception as e:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

    # Clear the cookie
    response = Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
    response.delete_cookie("refresh_token")

    return response