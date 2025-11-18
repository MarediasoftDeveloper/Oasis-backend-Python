from rest_framework import viewsets, permissions, status
from venue.Permissions.write_by_venue_only import WriteByVenueOnlySocialMedia
from rest_framework.response import Response
from app.Models.social_media_accounts import Social_Media_Accounts
from app.Serializers.social_media_acc_serializer import SocialMediaAccountsSerializer

class SocialMediaAccountVenueViewSet(viewsets.ModelViewSet):
    """
    A ViewSet to manage social media links for the authenticated user.
    """
    serializer_class = SocialMediaAccountsSerializer
    permission_classes = [permissions.IsAuthenticated, WriteByVenueOnlySocialMedia]

    def get_queryset(self):
        # Only return social media accounts belonging to the logged-in user
        return Social_Media_Accounts.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the user when creating a record
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Prevent changing ownership
        serializer.save(user=self.request.user)

 