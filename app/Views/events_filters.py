from httpx import request
from rest_framework.views import APIView
from app.Models.events import Events
from organisers.serializers.events_serializer import EventAppSerializer
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class EventFilters(APIView):

    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def post(self, request, *args, **kwargs):

        data = request.data

        start_date = data.get("start_date")
        category_id = data.get("category_id")

        events = (
            Events.objects
            .filter(
                status__in=[
                    "upcoming",
                    "live"
                ]
            )
            .order_by("event_start_date")
        )

        if start_date:
            start_date = parse_date(
                start_date
            )

            if start_date is None:
                return Response(
                    {
                        "error": (
                            "Invalid start_date. "
                            "Use YYYY-MM-DD."
                        )
                    },
                    status=400
                )

            weekday = start_date.weekday()

            events = events.filter(
                Q(
                    is_recurring=False,
                    event_start_date__lte=start_date,
                    event_close_date__gte=start_date
                )
                |
                Q(
                    is_recurring=True,
                    recurring_weekday=str(weekday)
                )
            )

        if category_id:
            events = events.filter(
                category_id=category_id
            )

        # ----------------------------------
        # Pagination
        # ----------------------------------

        paginator = self.pagination_class()

        page = paginator.paginate_queryset(
            events,
            request,
            view=self
        )

        serializer = EventAppSerializer(
            page,
            many=True,
            context={
                "request": request
            }
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    