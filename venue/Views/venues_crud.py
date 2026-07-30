from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from venue.models.venue_info import Venue_Info
from app.Models.events import Events
from venue.models.raffles import Raffles
from venue.models.rewards import Rewards
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from organisers.serializers.events_serializer import EventAppSerializer
from rest_framework import viewsets 
from rest_framework.response import Response 

class Venues_Crud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, WriteByVenueOnly]
    queryset = Venue_Info.objects.filter(status="approved")
    serializer_class=VenueInfoSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        data = serializer.data

        for venue in data:
            venue_id = venue.get("venue").get("id")
            has_active = (
                Raffles.objects.filter(venue__id=venue_id, is_ended=False).exists()
                or Rewards.objects.filter(venue__id=venue_id, is_ended=False).exists()
            )
    
            venue["has_active_raffle_or_reward"] = has_active

        return Response(data)


    def retrieve(self, request, *args, **kwargs):
        venue = self.get_object()

        serializer = self.get_serializer(venue)
        data = serializer.data
      
        participating_event_ids = VenuesParticipatingEvents.objects.filter(
            venues=venue.venue
        ).exclude(event__status="completed").values_list("event_id", flat=True).distinct()
        has_reward = Rewards.objects.filter(venue__id=venue.venue.id, is_ended=False).exists()
        events = Events.objects.filter(id__in=participating_event_ids)

        data["participating_events"] = EventAppSerializer(events, many=True).data
        data["has_reward"] = has_reward
        return Response(data)