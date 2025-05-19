from rest_framework import serializers
from .models import Task, Comment, Attachment
from projects.models import Project
from jwt_auth.models import CustomUser
from jwt_auth.serializers import UserSerializer
from .tasks import send_task_assignment_email


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model."""

    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at", "updated_at"]


class AttachmentSerializer(serializers.ModelSerializer):
    """Serializer for Attachment model."""

    uploaded_by = UserSerializer(read_only=True)
    file = serializers.FileField()

    class Meta:
        model = Attachment
        fields = ["id", "file", "uploaded_by", "uploaded_at"]


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""

    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_email = serializers.EmailField(write_only=True, required=False)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), source="project"
    )
    parent_task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source="parent_task",
        required=False,
        allow_null=True,
    )
    comments = CommentSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    deadline = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "project_id",
            "parent_task_id",
            "created_by",
            "assigned_to",
            "assigned_to_email",
            "created_at",
            "updated_at",
            "deadline",
            "comments",
            "attachments",
        ]

    def _assign_user_by_email(self, validated_data):
        """Helper to assign user by email if provided."""
        assigned_to_email = validated_data.pop("assigned_to_email", None)
        if assigned_to_email:
            try:
                validated_data["assigned_to"] = CustomUser.objects.get(
                    email=assigned_to_email
                )
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    {"assigned_to_email": "User not found"}
                )

    def create(self, validated_data):
        """Assign task to user by email if provided."""
        assigned_to_email = validated_data.get("assigned_to_email")
        self._assign_user_by_email(validated_data)
        validated_data["created_by"] = self.context["request"].user
        task = super().create(validated_data)
        if assigned_to_email and task.assigned_to:
            send_task_assignment_email.delay(task.id, task.assigned_to.email)
        return task

    def update(self, instance, validated_data):
        """Assigned user update"""
        assigned_to_email = validated_data.get("assigned_to_email")
        self._assign_user_by_email(validated_data)
        if "updated_by" not in validated_data:
            validated_data["updated_by"] = self.context["request"].user
        task = super().update(instance, validated_data)
        if (
            assigned_to_email
            and task.assigned_to
            and task.assigned_to.email != assigned_to_email
        ):
            send_task_assignment_email.delay(task.id, task.assigned_to.email)
        return task
