from rest_framework.views import APIView
from app.Models.events import Events
from organisers.serializers.events_serializer import EventAppSerializer
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from rest_framework.response import Response



class EventFilters(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        data = request.data

        start_date = data.get("start_date")
        
        events = Events.objects.filter(status__in=["upcoming", 'live'])

        if start_date:
            start_date = parse_date(start_date) 

       

        if start_date:

            weekday = start_date.weekday()
            events = events.filter(
                Q(
                    event_start_date__lte=start_date,
                    event_close_date__gte=start_date
                )
                |
                Q(
                    recurring_weekday=str(weekday)
                )
            )

            serializer = EventAppSerializer(
                events,
                many=True
            )

            return Response(
                serializer.data
            )  

        return Response({"message" : "No events found for this specific date or day!"}, status=status.HTTP_400_BAD_REQUEST)

    