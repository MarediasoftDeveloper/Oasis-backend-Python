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



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 3      
    page_size_query_param = 'page_size'
    max_page_size = 50


class EventsListView(APIView):
    permission_classes=[IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    

    def post(self, request):
        
        longitude = request.data.get('longitude') or None
        latitude = request.data.get('latitude') or None
        search = request.data.get('search') or None
        sort_by_date = request.data.get('sort_by_date')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        filter_options = request.data.get('filter_options')
        category_id = request.data.get('category_id')
        now = timezone.now()
        update_events = Events.objects.filter(event_close_date__lt=now).exclude(status='completed').update(status='completed')
        queryset = Events.objects.exclude(status__in=['draft', 'completed']).order_by('event_start_date')
        

        if filter_options == 'nearest' and longitude and latitude:
            longitude = float(longitude)
            latitude = float(latitude)

            queryset = queryset.annotate(
                distance=Min(
                    6371 * ACos(
                        Cos(Radians(latitude)) *
                        Cos(Radians(F('venuesparticipatingevents__venues__venue_profile__latitude'))) *
                        Cos(Radians(F('venuesparticipatingevents__venues__venue_profile__longitude')) - Radians(longitude)) +
                        Sin(Radians(latitude)) *
                        Sin(Radians(F('venuesparticipatingevents__venues__venue_profile__latitude')))
                    )
                )
            ).order_by('distance')

        elif filter_options == 'upcoming':
            queryset = queryset.filter(status='upcoming')

        elif filter_options == 'live':
            queryset = queryset.filter(status='live')
        else: 
            if sort_by_date == 'desc':
                queryset = queryset.order_by('-event_start_date')
            else:
                queryset = queryset.annotate(
                    status_order=Case(
                        When(status='live', then=1),
                        When(status='upcoming', then=2),
                        When(status='completed', then=3),
                        default=4,
                        output_field=IntegerField()
                    )
                ).order_by('status_order')
                
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Search
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(venuesparticipatingevents__venues__venue_profile__venue_name__icontains=search) |
                Q(created_by__username__icontains=search) |
                Q(created_by__first_name__icontains=search) |
                Q(created_by__last_name__icontains=search)
            ).distinct()

        
        if category_id: 
            queryset = queryset.filter(category__id=category_id)
        
        # Date filtering
        if start_date and not end_date:
            queryset = queryset.filter(event_start_date__date__gte=start_date)
        elif end_date and not start_date:
            queryset = queryset.filter(event_close_date__date__lte=end_date)
        elif start_date and end_date:
            queryset = queryset.filter(
                event_start_date__date__gte=start_date,
                event_close_date__date__lte=end_date
            )
         # PAGINATION START
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        if page is not None:
            serializer = EventAppSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

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
