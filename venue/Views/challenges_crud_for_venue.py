from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from venue.models.challenges import Challenges
from app.Models.challenge_achiever import Challenge_Achiever
from venue.Serializers.challenge_serializer import VenueChallengesSerializer
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.venue_only_permission import Request_By_Venue_Only
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from django.db.models import Count, Sum

class Challenges_Crud_for_Venue(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Venue_Only]
    serializer_class = VenueChallengesSerializer

    def get_queryset(self):
        """Return challenges belonging to the logged-in venue."""
        return Challenges.objects.filter(venue=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Serialize the queryset properly
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data 

        # Count approved challenges
        challenges_active = queryset.filter(is_approved='approved').count()

        scan_counts = (
            Challenge_Achiever.objects
            .filter(challenge__in=queryset)
            .values('challenge')
            .annotate(scans=Count('id'))
        )
        
        point_counts = (
            Challenge_Achiever.objects
            .filter(challenge__in=queryset)
            .values('challenge')
            .annotate(issued_points=Sum('points_issued'))
        )
        
        # All achievers for this venue’s challenges
        challenges_achieved = Challenge_Achiever.objects.filter(challenge__venue=self.request.user)
        
        unique_users = challenges_achieved.values("customer_taken").distinct().count()

        # Convert scan counts to a dictionary: {challenge_id: scans}
        scans_map = {item['challenge']: item['scans'] for item in scan_counts}
        points_map = {item['challenge']: item['issued_points'] for item in point_counts}

        # Inject scans into serialized data
        for item in data:
            challenge_id = item['id']
            item['scans'] = scans_map.get(challenge_id, 0)
            item['issued_points'] = points_map.get(challenge_id, 0)
            
           

        # Sum of all winning points issued across achievers
        total_points_issued = sum([item.points_issued for item in challenges_achieved])

        # Build custom response
        data = {
            "challenges": serializer.data,
            "summary": {
                "active_challenges": challenges_active,
                "total_challenges": queryset.count(),
                "total_scans": challenges_achieved.count(),
                "total_points_issued": total_points_issued,
                "unique_users": unique_users
            }
        }

        return Response(data, status=200)

    def perform_create(self, serializer):
        """Automatically assign venue when creating a challenge."""
        serializer.save(venue=self.request.user)
    

