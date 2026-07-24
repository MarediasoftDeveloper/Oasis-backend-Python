from datetime import datetime

from rest_framework import generics 
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Models.event_posts import EventPosts
from app.Models.event_attendees import EventAttendees
from app.Models.trails.trailModel import Trail
from app.Serializers.trailSerializers.trail_serializers import TrailSerializer, TrailGetSerializer
from app.Serializers.trailSerializers.trailstep_serializer import TrailStepSerializer
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
from django.db.models import Q, F, Prefetch, FloatField, Min, Case, When, IntegerField, Count
from django.db.models.functions import ACos, Cos, Sin, Radians
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10        
    page_size_query_param = 'page_size'
    max_page_size = 50


# class TrailListView(generics.ListAPIView):
#     permission_classes=[IsAuthenticated]
#     pagination_class = StandardResultsSetPagination
#     serializer_class = TrailGetSerializer
#     queryset = (
#         Trail.objects
#         .select_related(
#             "created_by",
#             "created_by__customer_profile",
#             "reward",
#             "badge",
#         )
#         .annotate(
#             steps_count=Count("steps", distinct=True)
#         )
#         .order_by("-created_at")
#     )



class TrailViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination


    def get_serializer_class(self):
        if self.action == "list":
            return TrailGetSerializer

        if self.action == "retrieve":
            return TrailSerializer

        # Used for create, update and partial_update
        return TrailSerializer

    def get_queryset(self):
        queryset = Trail.objects.all()

        if self.action == "list":
            return (
                queryset
                .select_related(
                    "reward",
                    "badge",
                    "created_by",
                    "created_by__customer_profile",
                )
                .annotate(
                    steps_count=Count("steps", distinct=True)
                )
                .order_by("-created_at")
            )

        if self.action == "retrieve":
            return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serialized_data = serializer.data
        serialized_data["steps"] = TrailStepSerializer(
            instance.steps.all(),
            many=True,
        ).data
        return Response(serialized_data)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)