from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Models.event_attendees import EventAttendees
from venue.models.raffles import Raffles
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only
from app.Permissions.send_by_customer_only import Request_By_Customer_Only



class EventParticipatingVenuesAppView(APIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]

    def get(self, request, id):
        queryset = VenuesParticipatingEvents.objects.filter(event__id=id)

        if not queryset.exists():
            return Response(
                {"message": "No participating venues found for this event."},
                status=404
            )

        is_event_attended = EventAttendees.objects.filter(
            event__id=id,
            user=request.user
        ).first()

        #  If user has NOT attended → simple response
        if not is_event_attended:
            return Response(
                EventAppVenuesParticipatingSerializer(queryset, many=True).data
            )

        participants = []

        for venue_obj in queryset:
            # Safe date handling
            start_date = max(venue_obj.available_from, is_event_attended.joined_at)

            end_date = venue_obj.available_till

            challenges_qs = Challenge_Achiever.objects.filter(
                challenge__venue=venue_obj.venues,
                customer_taken=request.user,
                scanned_at__gte=start_date,
            )

            if end_date:
                challenges_qs = challenges_qs.filter(scanned_at__lte=end_date)

            challenges_achieved = challenges_qs.count()

            # Serialize FIRST
            participant = EventAppVenuesParticipatingSerializer(venue_obj).data

            # Add extra fields
            participant['challenges_achieved'] = challenges_achieved
            participant['message'] = f"You have done {challenges_achieved} scans in this venue"

            # Always include field
            participant['has_raffles'] = Raffles.objects.filter(
                venue=venue_obj.venues
            ).exists()

            participants.append(participant)

        return Response(participants)
        


