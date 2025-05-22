from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer
from .models import Task, Comment, Attachment
from projects.models import Project, TaskStatus, Sprint
from projects.serializers import TaskStatusSerializer, SprintSerializer
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
    assigned_to_email = serializers.EmailField(
        write_only=True,
        required=False,
        help_text="Email of user to assign task to",
    )
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source="project",
        help_text="Project ID",
    )
    parent_task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source="parent_task",
        required=False,
        allow_null=True,
        help_text="Parent task ID for subtasks",
    )
    comments = CommentSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    deadline = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Task deadline (ISO 8601 format)",
    )
    status = TaskStatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=TaskStatus.objects.all(),
        source="status",
        required=False,
        allow_null=True,
        help_text="Task status ID",
    )
    sprint = SprintSerializer(read_only=True)
    sprint_id = serializers.PrimaryKeyRelatedField(
        queryset=Sprint.objects.all(),
        source="sprint",
        required=False,
        allow_null=True,
        help_text="Sprint ID",
    )
    estimated_hours = serializers.FloatField(
        default=0.0, help_text="Estimated hours to complete task"
    )
    actual_hours = serializers.FloatField(
        default=0.0, help_text="Actual hours spent on task"
    )
    story_points = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Story points for agile estimation",
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "status_id",
            "priority",
            "project_id",
            "parent_task_id",
            "created_by",
            "assigned_to",
            "assigned_to_email",
            "deadline",
            "estimated_hours",
            "actual_hours",
            "sprint",
            "sprint_id",
            "story_points",
            "comments",
            "attachments",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "title": {"help_text": "Task title (max 250 characters)"},
            "description": {"help_text": "Optional task description"},
            "priority": {"help_text": "Task priority (low, medium, high)"},
        }

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
