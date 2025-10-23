from rest_framework.permissions import BasePermission, SAFE_METHODS


class WriteByCustomerOnly(BasePermission):
  
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow read-only access
        if request.method in SAFE_METHODS:
            return True

        # Venues can edit only their own objects
        return user.user_role == "1" and obj.customer == user
