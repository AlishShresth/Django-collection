from rest_framework import serializers
from .models import Project
from jwt_auth.serializers import UserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""

    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    member_emails = serializers.ListField(
        child=serializers.EmailField(), write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "members",
            "member_emails",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Create project and assign members by email."""
        member_emails = validated_data.pop("member_emails", [])
        project = Project.objects.create(**validated_data)
        from jwt_auth.models import CustomUser

        for email in member_emails:
            try:
                user = CustomUser.objects.get(email=email)
                project.members.add(user)
            except CustomUser.DoesNotExist:
                pass  # Silently skip invalid emails
        return project
