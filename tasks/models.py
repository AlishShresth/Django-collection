from django.db import models
from jwt_auth.models import CustomUser


class Task(models.Model):
    """Model representing a task in the system."""

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
        ],
        default="todo",
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
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="created_tasks"
    )
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
