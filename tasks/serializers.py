from rest_framework import serializers
from .models import Task
from jwt_auth.serializers import UserSerializer


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""

    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "created_by",
            "assigned_to",
            "assigned_to_email",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Assign task to user by email if provided."""
        assigned_to_email = validated_data.pop("assigned_to_email", None)
        if assigned_to_email:
            from auth.models import CustomUser

            try:
                validated_data["assigned_to"] = CustomUser.objects.get(
                    email=assigned_to_email
                )
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    {"assigned_to_email": "User not found"}
                )

        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
