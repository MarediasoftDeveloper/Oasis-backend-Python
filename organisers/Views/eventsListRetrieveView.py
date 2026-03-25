from rest_framework import generics 
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Models.event_posts import EventPosts
from app.Models.event_attendees import EventAttendees
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from app.Models.events import Events
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from venue.models.badges import BadgesLevel
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from organisers.serializers.events_attendees_serializer import EventAppAttendeesSerializer
from organisers.serializers.events_posts_serializer import EventAppPostsSerializer
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from organisers.serializers.events_serializer import EventAppSerializer
from django.db.models.expressions import RawSQL

class EventsListView(APIView):
    permission_classes=[IsAuthenticated, Request_By_Customer_Only]

    def post(self, request):
        
        longitude = request.data.get('longitude') or None
        latitude = request.data.get('latitude') or None

        queryset = Events.objects.exclude(status='draft')

        if longitude is not None and latitude is not None:
            longitude = float(longitude)
            latitude = float(latitude)
            queryset = queryset.annotate(
                distance=RawSQL(
                    """
                    6371 * acos(
                        cos(radians(%s)) *
                        cos(radians(latitude)) *
                        cos(radians(longitude) - radians(%s)) +
                        sin(radians(%s)) *
                        sin(radians(latitude))
                    )
                    """,
                    (latitude, longitude, latitude),
                )
            ).order_by('distance')

        serializer = EventAppSerializer(queryset, many=True)

        return Response(serializer.data)

    




from rest_framework.response import Response

class EventsRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Events.objects.all().exclude(status='draft')
    serializer_class = EventAppSerializer

    def retrieve(self, request, *args, **kwargs):
        event = self.get_object()

        # Serialize main event
        event_serializer = self.get_serializer(event)

        # Fetch related data
        event_posts = EventPosts.objects.filter(event=event).order_by('-id')
        participating_venues = VenuesParticipatingEvents.objects.filter(event=event).order_by('-id')
        event_attendees = EventAttendees.objects.filter(event=event).order_by('-id')

        badge = None
        if event.badge:
            badge = BadgesLevel.objects.filter(badge=event.badge).first()

        # Serialize related data
        event_posts_serializer = EventAppPostsSerializer(event_posts, many=True)
        event_participated_serializer = EventAppVenuesParticipatingSerializer(participating_venues, many=True)
        event_attendees_serializer = EventAppAttendeesSerializer(event_attendees, many=True)
        badge_serializer = BadgesLevelSerializer(badge) if badge else None

        return Response({
            **event_serializer.data,
            "event_posts": event_posts_serializer.data,
            "venue_participating": event_participated_serializer.data,
            "event_attendees": event_attendees_serializer.data,
            "badge_level": badge_serializer.data if badge_serializer else None,
        })
