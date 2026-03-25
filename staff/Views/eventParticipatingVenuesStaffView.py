from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Models.event_attendees import EventAttendees
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only




class EventParticipatingVenuesStaffView(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_And_Organiser_Only]
    
    def post(self, request):
        
        user = request.data.get('user')
        event = request.data.get('event')
        queryset = VenuesParticipatingEvents.objects.filter(event__id=event)
        
        if not queryset.exists():
            return Response({"message": "No participating venues found for this event."}, status=404)

        isEventAttended = EventAttendees.objects.filter(event__id=event, user__id=user).first()
        participants = []
        if isEventAttended:
            name = f"{isEventAttended.user.first_name} {isEventAttended.user.last_name}" if isEventAttended.user.first_name else isEventAttended.user.username
            for particiapating_venue in queryset:
                end_date = min(
                    particiapating_venue.event.event_close_date,
                    particiapating_venue.available_till
                ) if particiapating_venue.available_till else particiapating_venue.event.event_close_date

                challenges_achieved = Challenge_Achiever.objects.filter(
                    challenge__venue=particiapating_venue.venues,
                    customer_taken__id=user,
                    scanned_at__gte=particiapating_venue.event.event_start_date,
                    scanned_at__lte=end_date,
                ).count() or 0
                
                participant =  EventAppVenuesParticipatingSerializer(particiapating_venue).data
                participant['challenges_achieved'] = challenges_achieved
                participant['message'] = f"{name} have done {challenges_achieved} scans in this venue, {particiapating_venue.scans_to_achieve_next_tier - challenges_achieved if challenges_achieved < particiapating_venue.scans_to_achieve_next_tier else 0} remaining scans in this venue."
                participants.append(participant)
        
            return Response(participants)
        print(EventAppVenuesParticipatingSerializer(queryset, many=True).data)
        return Response(EventAppVenuesParticipatingSerializer(queryset, many=True).data)

        


