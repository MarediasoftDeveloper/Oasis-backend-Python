from rest_framework import generics 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Models.event_posts import EventPosts
from app.Models.event_attendees import EventAttendees
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from app.Models.event_posts import EventPosts
from venue.models.badges import BadgesLevel
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from organisers.serializers.events_attendees_serializer import EventAppAttendeesSerializer
from organisers.serializers.events_posts_serializer import EventAppPostsSerializer
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from organisers.serializers.events_posts_serializer import EventAppPostsSerializer
from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only
from staff.Permissions.adminOrganiserVenueOnlyPermission import Request_By_Admin_Venue_And_Organiser_Only



class EventPostCreateStaffView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated, Request_By_Admin_Venue_And_Organiser_Only]
    queryset = EventPosts.objects.all()
    serializer_class = EventAppPostsSerializer

