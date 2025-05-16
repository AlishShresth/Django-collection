from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwnerOrAdmin


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task CRUD operations."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save()
