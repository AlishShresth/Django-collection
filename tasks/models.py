import os
from django.db import models
from django.core.validators import FileExtensionValidator
from jwt_auth.models import CustomUser
from projects.models import Project, TaskStatus, Sprint


class Task(models.Model):
    """Model representing a task in the system."""

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    status = models.ForeignKey(
        TaskStatus, on_delete=models.SET_NULL, null=True, related_name="tasks"
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        default="medium",
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    parent_task = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="subtasks"
    )
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="created_tasks"
    )
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        db_index=True,
    )
    deadline = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.FloatField(default=0.0)
    actual_hours = models.FloatField(default=0.0)
    sprint = models.ForeignKey(
        Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )
    story_points = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        unique_together = [("project", "title")]
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["parent_task"]),
            models.Index(fields=["assigned_to"]),
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["deadline"]),
        ]


class Comment(models.Model):
    """Model for task comments."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.email} on {self.task.title}"

    class Meta:
        ordering = ["-updated_at", "-created_at"]
        indexes = [
            models.Index(fields=["task"]),
            models.Index(fields=["author"]),
        ]


def task_attachment_path(instance, filename):
    """Generate file path for task attachments."""
    return f"attachments/task_{instance.task.id}/{filename}"


class Attachment(models.Model):
    """Model for task attachments."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(
        upload_to=task_attachment_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "docx", "jpg", "png", "jpeg"]
            )
        ],
    )
    uploaded_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="attachments"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return os.path.basename(self.file.name)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [models.Index(fields=["task"]), models.Index(fields=["uploaded_by"])]


class TaskHistory(models.Model):
    """Model to track changes to tasks."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="history")
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="task_changes"
    )
    field = models.CharField(max_length=100)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.field} changed on {self.task.title} at {self.changed_at}"
