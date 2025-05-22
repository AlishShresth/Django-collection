from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        help_text="Password (minimum 8 characters)",
    )
    password2 = serializers.CharField(
        write_only=True, required=True, help_text="Confirm password"
    )

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "password2",
        ]
        extra_kwargs = {
            "email": {"help_text": "Unique email address"},
            "phone_number": {"help_text": "Optional phone number (e.g., +1234567890)"},
        }

    def validate(self, data):
        """Ensure passwords match and meet requirements."""
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords must match"})
        validate_password(data["password"])
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Create a new user with hashed password."""
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data."""

    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "phone_number"]
