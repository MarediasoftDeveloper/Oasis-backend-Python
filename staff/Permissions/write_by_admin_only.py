from rest_framework.permissions import BasePermission, SAFE_METHODS


class WriteByAdminOnly(BasePermission):
  
    def has_object_permission(self, request, view, obj):
        user = request.user

        return user.user_role == "3" and user.is_superuser






    

class WriteByAdminOnlyCustom(BasePermission):
  
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in SAFE_METHODS:
            return user.user_role == "3" and user.is_superuser

        # Admin can edit only their own objects
        return user.user_role == "3" and user.is_superuser and obj == user