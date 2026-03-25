from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from venue.models.challenges import Challenges
from app.Models.challenge_achiever import Challenge_Achiever
from venue.Serializers.challenge_serializer import StaffChallengesSerializer
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.renderers import JSONRenderer


class Challenges_Crud_for_Staff(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    queryset = Challenges.objects.all().order_by('-created_at')
    serializer_class = StaffChallengesSerializer
 

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Serialize the queryset properly
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data 

        now = timezone.now()

        challenges_active = queryset.filter(
            is_approved='approved',
            ending_at__gte=now
        ).count()

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
        challenges_achieved = Challenge_Achiever.objects.all()
        
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
    
    
    

