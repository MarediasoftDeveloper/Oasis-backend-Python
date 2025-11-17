from rest_framework.permissions import BasePermission


class Request_By_Venue_Only(BasePermission):
    """
    Allows access only to authenticated users who are not in Staff_Info.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.user_role in ['1','3']:
            return False
        return True




class Request_By_Current_Venue_Only(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Must be venue user
        if user.user_role != "2":
            return False

        # Object must belong to this venue
        return hasattr(obj, "venue") and obj.venue == user
