from rest_framework.permissions import BasePermission, SAFE_METHODS

class WriteByAdminAndVenueOnly(BasePermission):
  
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow read-only access
        if request.method in SAFE_METHODS:
            return True

        # Admins can edit everything
        if user.is_superuser:
            return True

        # Venues can edit only their own objects
        return user.user_role == "2" and obj.venue == user
