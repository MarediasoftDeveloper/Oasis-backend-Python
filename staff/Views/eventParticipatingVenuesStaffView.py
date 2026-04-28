from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Models.event_attendees import EventAttendees
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from organisers.serializers.events_venue_participating import EventAppVenuesParticipatingSerializer
from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only
import venue




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
        total_completed_scans = 0
        if isEventAttended:
            name = f"{isEventAttended.user.first_name} {isEventAttended.user.last_name}" if isEventAttended.user.first_name else isEventAttended.user.username
            for particiapating_venue in queryset:
                start_date = max(particiapating_venue.available_from, isEventAttended.joined_at)

                challenges_achieved = Challenge_Achiever.objects.filter(
                    challenge__venue=particiapating_venue.venues,
                    customer_taken__id=user,
                    scanned_at__gte=start_date,
                    scanned_at__lte=particiapating_venue.available_till,
                ).count() or 0
                
                participant =  EventAppVenuesParticipatingSerializer(particiapating_venue).data
                total_completed_scans += challenges_achieved
                
                participant['challenges_achieved'] = challenges_achieved
                participant['message'] = f"{name} have done {challenges_achieved} scans in this venue"
                participants.append(participant)
        
            participants.append({"total_completed_scans": total_completed_scans})
            return Response(participants)
       
        return Response(EventAppVenuesParticipatingSerializer(queryset, many=True).data)

        


