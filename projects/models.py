from django.db import models
from jwt_auth.models import CustomUser


class Project(models.Model):
    """Model representing a project for task organization."""

    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="owned_projects"
    )
    members = models.ManyToManyField(CustomUser, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("name", "owner")]
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name", "owner"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["updated_at"]),
            models.Index(fields=["owner"]),
        ]

    def __str__(self):
        return self.name


class TaskStatus(models.Model):
    """Model for custom task statuses per project."""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="statuses"
    )
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)  # For Kanban sorting

    class Meta:
        unique_together = ["project", "name"]
        indexes = [models.Index(fields=["project", "name"])]
        ordering = ["order"]
