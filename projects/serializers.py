from django.db import transaction
from rest_framework import serializers
from .models import Project
from jwt_auth.serializers import UserSerializer
from jwt_auth.models import CustomUser


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

    @transaction.atomic
    def create(self, validated_data):
        """Create project and assign members by email."""
        member_emails = validated_data.pop("member_emails", [])
        project = Project.objects.create(**validated_data)

        if member_emails:
            # fetch all users with the given emails in a single query
            users_to_add = list(CustomUser.objects.filter(email__in=member_emails))

            # check if all provided emails correspond to existing users
            found_emails = {user.email for user in users_to_add}
            invalid_emails = [
                email for email in member_emails if email not in found_emails
            ]

            if invalid_emails:
                # raise validation error for invalid emails
                raise serializers.ValidationError(
                    {
                        "member_emails": f"User with these emails not found: {', '.join(invalid_emails)}"
                    }
                )

            # add all found users to the project members in one go
            project.members.set(users_to_add)  # use set() for efficiency
        return project

    def update(self, instance, validated_data):
        member_emails = validated_data.pop("member_emails", None)
        # handle other updates
        instance = super().update(instance, validated_data)
        if member_emails is not None:
            users_to_set = list(CustomUser.objects.filter(email__in=member_emails))
            found_emails = {user.email for user in users_to_set}
            invalid_emails = [
                email for email in member_emails if email not in found_emails
            ]
            if invalid_emails:
                raise serializers.ValidationError(
                    {
                        "member_emails": f"Users with these emails not found: {', '.join(invalid_emails)}"
                    }
                )
            instance.members.set(users_to_set)
        return instance