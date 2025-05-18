from rest_framework import permissions


class IsProjectOwnerOrMember(permissions.BasePermission):
    """Allow only project owner or members to access; only owner/admin can edit."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.members.contains(request.user) or request.user.is_staff
        return obj.owner == request.user or request.user.is_staff
