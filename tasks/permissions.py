from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow only task creator or admin to edit/delete"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user or request.user.is_staff