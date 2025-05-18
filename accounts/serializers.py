from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "date_joined", "profile_picture"]
        read_only_fields = ['profile_picture_url']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None
        

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True, min_length=8)

    
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "password", "password_confirmation"]

    def validate(self, data):
        if data["password"] != data["password_confirmation"]:
            raise serializers.ValidationError({"password_confirmation": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirmation")  # Remove password_confirmation since it's not in the model
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"]
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        return user 
    

class UpdateUsernameSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, min_length=3, max_length=150)

    def validate_username(self, value):
        # Check if username already exists
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value