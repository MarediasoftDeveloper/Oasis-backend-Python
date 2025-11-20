from rest_framework.views import APIView
from rest_framework import viewsets
from venue.models.venue_badges import Venue_Badges
from venue.models.badges import BadgesLevel
from venue.models.challenges import Challenges
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from venue.Serializers.venue_badges_serializer import VenueBadgesSerializer
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from rest_framework.permissions import IsAuthenticated
from venue.Permissions.venue_only_permission import Request_By_Current_Venue_Only
from app.models import Customer
from venue.models.venue_info import Venue_Info
from rest_framework.response import Response
from datetime import timedelta
from datetime import timezone
import datetime
from venue.models.venue_opening_hours import Venue_Opening_Hours


class Venue_Badge_CRUD(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        venues = Customer.objects.filter(user_role='2')
        data = []

        for venue in venues:
            venue_info = Venue_Info.objects.filter(venue=venue).first()

            # Active venue badges
            venue_badges = (
                Venue_Badges.objects
                .filter(venue=venue, is_active=True)
                .values_list('badge__id', flat=True)
            )

            # Badge levels (only category=1)
            badges = BadgesLevel.objects.filter(
                badge__id__in=venue_badges,
                category_id=1
            )
            today = datetime.datetime.now()

            # Get the full weekday name
            day_of_week_attr = today.strftime("%A").lower()
             
            
            hours = Venue_Opening_Hours.objects.filter(venue=venue).first()
            if hours:
                # Get the value of the attribute corresponding to the current day
                # We use None as a default value if the attribute is somehow missing
                daily_hours = getattr(hours, day_of_week_attr, None)
            else:
                daily_hours = None
            venue_info_data = VenueInfoSerializer(venue_info).data if venue_info else None
            venue_badges_data = BadgesLevelSerializer(badges, many=True).data if badges.exists() else []

            data.append({
                "venue_profile": venue_info_data,
                "venue_badges": venue_badges_data,
                "daily_hours": daily_hours
            })
            

        return Response(data)


 
 
class Venue_Badge_CRUD_Retrieve(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, venue_id):
        try:
            # Only venue users (user_role = 2)
            venue = Customer.objects.get(id=venue_id, user_role='2')
        except Customer.DoesNotExist:
            return Response({"error": "Venue not found or not valid!"}, status=404)

        # Fetch venue profile
        venue_info = Venue_Info.objects.filter(venue=venue).first()
        venue_info_data = VenueInfoSerializer(venue_info).data if venue_info else None
  
        # Fetch the venue's active badges   
        venue_badge_ids = (
            Venue_Badges.objects
            .filter(venue=venue, is_active=True)
            .values_list('badge_id', flat=True)
        )
        today = datetime.datetime.now()

        # Get the full weekday name
        day_of_week_attr = today.strftime("%A").lower()
            
        
        hours = Venue_Opening_Hours.objects.filter(venue=venue).first()
        if hours:
            # Get the value of the attribute corresponding to the current day
            # We use None as a default value if the attribute is somehow missing
            daily_hours = getattr(hours, day_of_week_attr, None)
        else:
            daily_hours = None
        badges = BadgesLevel.objects.filter(
            badge__id__in=venue_badge_ids,
            category_id=1
        )

        venue_badges_data = BadgesLevelSerializer(badges, many=True).data

        return Response({
            "venue_profile": venue_info_data,
            "venue_badges": venue_badges_data,
            "daily_hours": daily_hours
        })

 

class Venue_Badge_list_for_dashboard(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, Request_By_Current_Venue_Only]
    serializer_class=VenueBadgesSerializer

    def get_queryset(self):
        return Venue_Badges.objects.filter(venue=self.request.user)

    def list(self, request):
        queryset=self.get_queryset()
        try:
            venue_badges = queryset.values_list('badge__id', flat=True)
            selected_badges = BadgesLevel.objects.filter(badge__in=venue_badges, category=1) 
            venue_badges_data = BadgesLevelSerializer(selected_badges, many=True)
            unselected_badges = BadgesLevel.objects.filter(
                category=1
            ).exclude(
                badge__id__in=venue_badges
            )
            unselected_badges_data = BadgesLevelSerializer(unselected_badges, many=True)


            # Append to the main list
           
        except Customer.DoesNotExist:
            return Response({"error":"User is not valid!"})

        return Response({"selected_badges":venue_badges_data.data,
                         "unselected_badges": unselected_badges_data.data
                         })
    
    def get_object(self):
        queryset=self.get_queryset()
        badge_id = self.kwargs.get('pk')
        return queryset.get(badge__id=badge_id)

    
    def perform_create(self, serializer):
        serializer.save(venue=self.request.user)

 

class Venue_Badges_list_for_challenge(APIView):
    permission_classes = [IsAuthenticated, Request_By_Current_Venue_Only]
    
    def get(self, request):
        try:
            venue_badges = Venue_Badges.objects.filter(venue=self.request.user).values_list('badge__id', flat=True)
            selected_badges = BadgesLevel.objects.filter(badge__in=venue_badges, category=1) 
            venue_badges_data = BadgesLevelSerializer(selected_badges, many=True)
          

            # Append to the main list
           
        except Customer.DoesNotExist:
            return Response({"error":"User is not valid!"})

        return Response({"badges":venue_badges_data.data})
    
    