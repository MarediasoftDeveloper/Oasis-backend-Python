from rest_framework.permissions import BasePermission


class Request_By_Admin_Venue_And_Organiser_Only(BasePermission):
    """
    Allows access only to authenticated users who are not in Staff_Info.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.user_role == '1':
            return False
        return True







