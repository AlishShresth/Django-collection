from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .models import Task, Comment, Attachment
from .serializers import TaskSerializer, CommentSerializer, AttachmentSerializer
from .permissions import IsOwnerOrAdmin


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task CRUD operations."""

    queryset = Task.objects.select_related(
        "project", "parent_task", "created_by", "assigned_to"
    ).prefetch_related("comments", "attachments")
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "assigned_to__email"]
    ordering_fields = ["created_at", "priority"]
    ordering = ["-updated_at"]

    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save()

    @action(detail=True, methods=["post"], serializer_class=CommentSerializer)
    def add_comment(self, request, pk=None):
        """Add a comment to a task."""
        task = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], serializer_class=AttachmentSerializer)
    def add_attachment(self, request, pk=None):
        """Add an attachment to a task."""
        task = self.get_object()
        serializer = AttachmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(task=task, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
