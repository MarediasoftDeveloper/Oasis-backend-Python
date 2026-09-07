from django.contrib.admin import filters
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
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, filters


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 15               
    page_size_query_param = 'page_size'
    max_page_size = 50


class Venues_Crud(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        WriteByVenueOnly
    ]

    queryset = (
        Venue_Info.objects
        .exclude(
            status__in=[
                "suspended",
                "pending"
            ]
        )
        .order_by(
            "-add_to_popular",
            "venue_name"
        )
    )

    serializer_class = VenueInfoSerializer

    filter_backends = [
        filters.SearchFilter
    ]

    search_fields = [
        "venue_name"
    ]

    pagination_class = (
        StandardResultsSetPagination
    )

    def list(
        self,
        request,
        *args,
        **kwargs
    ):
        # IMPORTANT:
        # filter_queryset makes SearchFilter work.
        queryset = self.filter_queryset(
            self.get_queryset()
        )

        page = self.paginate_queryset(
            queryset
        )

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True
            )

            data = serializer.data

        else:
            serializer = self.get_serializer(
                queryset,
                many=True
            )

            data = serializer.data

        # ------------------------------------------
        # Get all venue IDs from current response
        # ------------------------------------------

        venue_ids = []

        for venue in data:

            venue_data = venue.get(
                "venue"
            ) or {}

            venue_id = venue_data.get(
                "id"
            )

            if venue_id is not None:
                venue_ids.append(
                    venue_id
                )

        # ------------------------------------------
        # Get active raffle venues
        # ONE query
        # ------------------------------------------

        active_raffle_venue_ids = set(
            Raffles.objects
            .filter(
                venue_id__in=venue_ids,
                is_ended=False
            )
            .values_list(
                "venue_id",
                flat=True
            )
        )

        # ------------------------------------------
        # Get active reward venues
        # ONE query
        # ------------------------------------------

        active_reward_venue_ids = set(
            Rewards.objects
            .filter(
                venue_id__in=venue_ids,
                is_ended=False
            )
            .values_list(
                "venue_id",
                flat=True
            )
        )

        # Combine both sets
        active_venue_ids = (
            active_raffle_venue_ids
            | active_reward_venue_ids
        )

        # ------------------------------------------
        # Add field to serializer response
        # ------------------------------------------

        for venue in data:

            venue_data = venue.get(
                "venue"
            ) or {}

            venue_id = venue_data.get(
                "id"
            )

            venue[
                "has_active_raffle_or_reward"
            ] = (
                venue_id
                in active_venue_ids
            )

        # ------------------------------------------
        # Return paginated response
        # ------------------------------------------

        if page is not None:
            return self.get_paginated_response(
                data
            )

        return Response(
            data
        )


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