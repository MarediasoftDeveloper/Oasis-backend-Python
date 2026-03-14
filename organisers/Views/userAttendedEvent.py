from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Models.events import Events
from app.Models.event_posts import EventPosts
from app.Models.event_attendees import EventAttendees
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from app.Models.events import Events
from venue.models.badges import BadgesLevel
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from app.Models.event_badges_earned import EventBadgesEarned
from organisers.serializers.events_attendees_serializer import EventAppAttendeesSerializer
from organisers.serializers.events_posts_serializer import EventAppPostsSerializer
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from organisers.serializers.events_serializer import EventAppSerializer

class UserAttendedEventView(APIView):
    permission_classes=[IsAuthenticated, Request_By_Customer_Only]
    









        


    