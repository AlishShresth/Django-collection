from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Project, TaskStatus, Sprint
from .serializers import ProjectSerializer, TaskStatusSerializer, SprintSerializer
from .permissions import IsProjectOwnerOrMember


class ProjectViewSet(viewsets.ModelViewSet):
    """Viewset for Project CRUD operations."""

    queryset = Project.objects.select_related("owner").prefetch_related("members")
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrMember]

    def perform_create(self, serializer):
        """Set owner to current user."""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], serializer_class=TaskStatusSerializer)
    def add_status(self, request, pk=None):
        project = self.get_object()
        if project.owner != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )
        serializer = TaskStatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], serializer_class=SprintSerializer)
    def add_sprint(self, request, pk=None):
        project = self.get_object()
        if project.owner != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN
            )
        serializer = SprintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
