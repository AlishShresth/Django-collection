from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Project
from .serializers import ProjectSerializer
from .permissions import IsProjectOwnerOrMember


class ProjectViewSet(viewsets.ModelViewSet):
    """Viewset for Project CRUD operations."""

    queryset = Project.objects.select_related("owner").prefetch_related("members")
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrMember]

    def perform_create(self, serializer):
        """Set owner to current user."""
        serializer.save(owner=self.request.user)
