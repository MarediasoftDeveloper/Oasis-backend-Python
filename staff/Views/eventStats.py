from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Models.event_posts import EventPosts
from app.Models.event_attendees import EventAttendees
# from app.Models.event_badges_earned import EventBadgesEarned
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from app.Models.events import Events
from app.Models.challenge_achiever import Challenge_Achiever
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from venue.models.badges import BadgesLevel
from app.Models.event_posts import EventPosts
from venue.models.venue_info import Venue_Info
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from organisers.serializers.events_attendees_serializer import EventAppAttendeesSerializer
from organisers.serializers.events_posts_serializer import EventAppPostsSerializer
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from organisers.serializers.events_serializer import EventStaffSerializer
from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only 
from rest_framework import filters
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Count, Q
from app.Serializers.challenge_achiever_serializer import ChallengeAchieverSerializer

class EventStatsView(APIView):

    permission_classes = [IsAuthenticated, Request_By_Admin_And_Organiser_Only]

    def get(self, request):

        # Base Querysets
        Events_qs = Events.objects.all().order_by('-id')
        

        venues = VenuesParticipatingEvents.objects.filter(
            event__in=Events_qs
        ).select_related('event', 'venues')  # optimization

        # Event Counts
        total_active_events = Events_qs.filter(status='live').count()
        total_upcoming_events = Events_qs.filter(status='upcoming').count()
        total_complete_events = Events_qs.filter(status='completed').count()
        total_draft_events = Events_qs.filter(status='draft').count()
        total_events = Events_qs.count()

        # Date Handling
        now = timezone.now()
        last_month = now.month - 1 if now.month > 1 else 12
        year = now.year if now.month > 1 else now.year - 1

        # Attendees Stats
        total_attendees_current_month = EventAttendees.objects.filter(
            joined_at__year=now.year,
            joined_at__month=now.month
        ).count()

        total_attendees_last_month = EventAttendees.objects.filter(
            joined_at__year=year,
            joined_at__month=last_month
        ).count()

        difference = total_attendees_current_month - total_attendees_last_month

        if total_attendees_last_month > 0:
            attendees_percentage_change = (difference / total_attendees_last_month) * 100
        else:
            attendees_percentage_change = 0

        # Participating Venues
        participating_venues = venues.count()

        # Last 5 Months Stats
        five_months_ago = now - timedelta(days=150)

        attendees_last_5_months = (
            EventAttendees.objects
            .filter(joined_at__gte=five_months_ago)
            .annotate(month=TruncMonth("joined_at"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )

        attendees_monthly_stats = [
            {
                "month": item["month"].strftime("%B"),
                "attendees": item["total"]
            }
            for item in attendees_last_5_months
        ]

        # Preload Venue Info (avoid N+1 query)
        venue_info_map = {
            v.venue_id: v for v in Venue_Info.objects.filter(
                venue__in=[v.venues for v in venues]
            )
        }

        # Venue Challenges
        venue_challenges = {}
        total_scans = 0
        combined_q = Q()
        for venue in venues:
            # Fix: use minimum end date instead of duplicate lte
            end_date = min(
                venue.event.event_close_date,
                venue.available_till
            ) if venue.available_till else venue.event.event_close_date

            scans_qs = Challenge_Achiever.objects.filter(
                challenge__venue=venue.venues,
                scanned_at__gte=venue.event.event_start_date,
                scanned_at__lte=end_date
            )
            combined_q |= Q(
                challenge__venue=venue.venues,
                scanned_at__gte=venue.event.event_start_date,
                scanned_at__lte=end_date
            )
            scans_count = scans_qs.count()
            total_scans += scans_count

            if scans_count > 0:
                venue_info = venue_info_map.get(venue.venues.id)

                venue_challenges[str(venue.venues.id)] = {
                    "count": scans_count,
                    "venue_details": VenueInfoSerializer(venue_info).data if venue_info else None
                }

        # Recent Activities
        recent_activity_events_qs = Events_qs.order_by('-created_at')[:5]

        recent_attendees_qs = EventAttendees.objects.filter(
            event__in=Events_qs
        ).order_by('-joined_at')[:5]

        recent_scans_qs = Challenge_Achiever.objects.filter(
            combined_q
        ).order_by('-scanned_at')[:5]

        post_created_qs = EventPosts.objects.filter(
            event__in=Events_qs
        ).order_by('-created_at')[:5]

        # Serializers
        events_created_data = EventStaffSerializer(
            recent_activity_events_qs, many=True
        ).data

        recent_attendees_data = EventAppAttendeesSerializer(
            recent_attendees_qs, many=True
        ).data

        recent_post_created_data = EventAppPostsSerializer(
            post_created_qs, many=True
        ).data

        recent_scans_data = ChallengeAchieverSerializer(
            recent_scans_qs, many=True
        ).data

        return Response({
            "total_events": total_events,
            "total_active_events": total_active_events,
            "total_upcoming_events": total_upcoming_events,
            "total_draft_events": total_draft_events,
            "total_complete_events": total_complete_events,
            "total_attendees_current_month": total_attendees_current_month,
            "attendees_percentage_change": round(attendees_percentage_change, 2),
            "total_scans": total_scans,
            "total_participating_venues": participating_venues,
            "attendees_monthly_stats": attendees_monthly_stats,
            "venue_challenges": venue_challenges,
            "recent_activities": {
                "events_created": events_created_data,
                "recent_attendees": recent_attendees_data,
                "recent_scans": recent_scans_data,
                "recent_post_created": recent_post_created_data,
            }
        })