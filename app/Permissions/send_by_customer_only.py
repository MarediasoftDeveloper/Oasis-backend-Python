from rest_framework.permissions import BasePermission
from app.models import Customer
from staff.models.staff_info import Staff_Info 



class Request_By_Customer_Only(BasePermission):
    """
    Allows access only to authenticated users who are not in Staff_Info.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.user_role in ['2','3']:
            return False
        return True


