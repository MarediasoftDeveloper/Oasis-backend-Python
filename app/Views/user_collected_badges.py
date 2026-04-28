from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Serializers.earned_badges_by_user_serializer import Earned_Badges_By_User_Serializer
from venue.Serializers.challenge_serializer import ChallengesSerializer
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from rest_framework import status
from ..Models.earned_badges_by_user import Earned_Badges
from venue.models.badges import Badges, BadgesLevel
from venue.models.challenges import Challenges
from app.Models.events import Events
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.event_attendees import EventAttendees
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from django.utils import timezone
from django.db.models import Prefetch


class Collected_badges(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user
        # ---- Earned badges ----
        earned_badges = Earned_Badges.objects.filter(user=user)
        earned_badges_ids = set(
            earned_badges.values_list('badge__id', flat=True)
        )

        # ---- Events with participants (optimized) ----
        events = Events.objects.select_related('badge').prefetch_related(
            Prefetch(
                'venuesparticipatingevents_set',
                queryset=VenuesParticipatingEvents.objects.select_related('venues')
            )
        )

        collected_events = []
        uncollected_events = []

        user_scans = Challenge_Achiever.objects.filter(customer_taken=user)
        user_events = {
            ea.event_id: ea
            for ea in EventAttendees.objects.filter(user=user)
        }
        for event in events:

            participants = event.venuesparticipatingevents_set.all()

            has_achieved = False
            event_joined = user_events.get(event.id)

            # IMPORTANT: check per participant, decide per event
            for participant in participants:
                if event_joined:
                  start_date = max(participant.available_from, event_joined.joined_at)
                  if user_scans.filter(
                      challenge__venue=participant.venues,
                      scanned_at__gte=start_date,
                      scanned_at__lte=participant.available_till
                  ).exists():
                      has_achieved = True
                      break

            badge_qs = BadgesLevel.objects.filter(
                badge__id=event.badge.id,
                category__category__icontains='basic'
            )

            event_data = {
                "event_id": event.id,
                "badge": BadgesLevelSerializer(badge_qs, many=True).data,
            }

            if has_achieved:
                collected_events.append(event_data)
            else:
                uncollected_events.append(event_data)

        # ---- Collected badges ----
        collected_badges = []
        for badge_id in earned_badges_ids:

            badge_count = earned_badges.filter(badge__id=badge_id).count()

            badge_qs = BadgesLevel.objects.filter(
                badge__id=badge_id,
                category__category__icontains='basic'
            )

            collected_badges.append({
                "badge": BadgesLevelSerializer(badge_qs, many=True).data,
                "count": badge_count
            })

        # ---- Uncollected badges ----
        uncollected_badges_qs = BadgesLevel.objects.filter(
            category__category__icontains='basic'
        ).exclude(
            badge__id__in=earned_badges_ids
        )

        # ---- Final Response ----
        return Response({
            "event_badges": {
                "collected": collected_events,
                "uncollected": uncollected_events
            },
            "badges": {
                "collected": collected_badges,
                "uncollected": BadgesLevelSerializer(uncollected_badges_qs, many=True).data
            }
        })