from datetime import datetime

from rest_framework import generics 
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Models.event_posts import EventPosts
from app.Models.event_attendees import EventAttendees
from venue.models.venue_info import Venue_Info
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from app.Models.events import Events
from venue.models.badges import BadgesLevel
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from organisers.serializers.events_attendees_serializer import EventAppAttendeesSerializer
from organisers.serializers.events_posts_serializer import EventAppPostsSerializer
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from organisers.serializers.events_serializer import EventAppSerializer
from django.db.models.expressions import RawSQL
from django.db.models import Q, F, Prefetch, FloatField, Min, Case, When, IntegerField
from django.db.models.functions import ACos, Cos, Sin, Radians
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response



class RecurringEventsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Events.objects.filter(is_recurring=True).exclude(status__in=['draft', 'completed']).order_by('event_start_date')[0:10]
    serializer_class = EventAppSerializer
