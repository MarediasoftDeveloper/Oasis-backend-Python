from rest_framework import viewsets, permissions, status
from app.Permissions.write_by_customer_only_where_obj_user import WriteByCustomerOnlyUser
from rest_framework.response import Response
from app.Models.social_media_accounts import Social_Media_Accounts
from app.Serializers.social_media_acc_serializer import SocialMediaAccountsSerializer

class SocialMediaAccountViewSet(viewsets.ModelViewSet):
    """
    A ViewSet to manage social media links for the authenticated user.
    """
    serializer_class = SocialMediaAccountsSerializer
    permission_classes = [permissions.IsAuthenticated, WriteByCustomerOnlyUser]

    def get_queryset(self):
        return Social_Media_Accounts.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
       serializer.save(user=self.request.user)

 
