from rest_framework.permissions import BasePermission, SAFE_METHODS


class WriteByVenueOnly(BasePermission):
  
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow read-only access
        if request.method in SAFE_METHODS:
            return True

        # Venues can edit only their own objects
        return user.user_role == "2" and obj.venue == user



class WriteByVenueOnlySocialMedia(BasePermission):
  
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow read-only access
        if request.method in SAFE_METHODS:
            return user.user_role == "2" and obj.user == user

        # Venues can edit only their own objects
        return user.user_role == "2" and obj.user == user



class WriteByVenueOnlyMenuItem(BasePermission):
  
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow read-only access
        if request.method in SAFE_METHODS:
            return True

        # Venues can edit only their own objects
        return user.user_role == "2" and obj.menu_category.venue == user
    

class WriteByVenueOnlyCustom(BasePermission):
  
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow read-only access
        if request.method in SAFE_METHODS:
            return True

        # Venues can edit only their own objects
        return user.user_role == "2" and obj == user
    



class WriteByVenueAdminOnly(BasePermission):
  
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow read-only access
        if request.method in SAFE_METHODS:
            return True

        # Venues can edit only their own objects
        return user.user_role =="3" or obj.venue == user
