from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Models.event_attendees import EventAttendees
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
            return Response({"message": "No participating venues found for this event."}, status=404)

        isEventAttended = EventAttendees.objects.filter(event__id=id, user=request.user).first()
        participants = []
        if isEventAttended:
            for particiapating_venue in queryset:
                challenges_achieved = Challenge_Achiever.objects.filter(
                    challenge__venue=particiapating_venue.venues,
                    customer_taken=request.user,
                    scanned_at__lte=particiapating_venue.availabile_till,
                ).count() or 0
                participant =  EventAppVenuesParticipatingSerializer(particiapating_venue).data
                participant['challenges_achieved'] = challenges_achieved
                participant['message'] = f"You have done {challenges_achieved} scans in this venue, {particiapating_venue.scans_to_achieve_next_tier - challenges_achieved if challenges_achieved < particiapating_venue.scans_to_achieve_next_tier else 0} remaining scans in this venue."
                participants.append(participant)
        
            return Response(participants)
        
        return Response(EventAppVenuesParticipatingSerializer(queryset, many=True).data)

        


