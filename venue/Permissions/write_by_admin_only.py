from rest_framework.permissions import BasePermission, SAFE_METHODS


class WriteByAdminOnly(BasePermission):
 

    def has_permission(self, request, view):
        user = request.user

        # Allow read-only methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return user.is_authenticated  # Optional: only allow logged-in users to read

        # Allow writes only to superusers
        return user.is_authenticated and user.is_superuser
    






class WriteByAdminAndVenueOnly(BasePermission):
 

    def has_permission(self, request, view):
        user = request.user

        # Allow read-only methods (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return user.is_authenticated  # Optional: only allow logged-in users to read

        # Allow writes only to superusers
        return user.is_authenticated and user.is_superuser