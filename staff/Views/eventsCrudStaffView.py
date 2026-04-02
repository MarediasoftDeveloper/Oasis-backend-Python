from rest_framework import viewsets 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Models.event_posts import EventPosts
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.event_attendees import EventAttendees
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from app.Models.events import Events
from venue.models.badges import BadgesLevel
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from organisers.serializers.events_attendees_serializer import EventAppAttendeesSerializer
from organisers.serializers.events_posts_serializer import EventAppPostsSerializer
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from organisers.serializers.events_serializer import EventStaffSerializer
from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only 
from rest_framework import filters



class EventCrudStaffView(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated, Request_By_Admin_And_Organiser_Only]
    queryset = Events.objects.all().order_by('-id')
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'title',
        'venuesparticipatingevents__venues__venue_profile__venue_name',
        'created_by__username',
        'created_by__first_name',
        'created_by__last_name'
    ]
    
    serializer_class = EventStaffSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).distinct()   
        serializer = self.get_serializer(queryset, many=True)
        total_active_events = queryset.exclude(status='draft').count()
        total_events = queryset.count()
        participating_venues = VenuesParticipatingEvents.objects.filter(event__in=queryset)
        total_scans = 0

        for participating_venue in participating_venues:
            end_date = min(
                participating_venue.event.event_close_date,
                participating_venue.available_till
            ) if participating_venue.available_till else participating_venue.event.event_close_date

            total_scans += Challenge_Achiever.objects.filter(challenge__venue=participating_venue.venues, scanned_at__gte=participating_venue.event.event_start_date, scanned_at__lte=end_date).count()

        return Response({
            "total_events": total_events,
            "total_active_events": total_active_events,
            "total_scans": total_scans,
            "total_participating_venues": participating_venues.count(),
            "events": serializer.data
        })


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
            "total_participating_venues": participating_venues.count(),
            "total_event_attendees": event_attendees.count(),
            "event_attendees": event_attendees_serializer.data,
            "badge_level": badge_serializer.data if badge_serializer else None,
        })


    




