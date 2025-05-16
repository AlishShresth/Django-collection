from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwnerOrAdmin


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task CRUD operations."""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "assigned_to__email"]
    ordering_fields = ["created_at", "priority"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save()
