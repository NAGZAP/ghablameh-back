from rest_framework.permissions import BasePermission

class IsOrganizationAdmin(BasePermission):
    """
    Custom permission to only allow organization admins to access.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'organization_admin')
    



class IsNotOrganizationAdmin(BasePermission):
    """
    Custom permission to only allow organization admins to access.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and not hasattr(request.user, 'organization_admin')