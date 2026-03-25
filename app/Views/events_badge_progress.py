from math import floor

from rest_framework import generics
from rest_framework.views import APIView
from app.models import Customer_profile
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import calendar
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from app.Models.event_attendees import EventAttendees
from venue.models.challenges import Challenges
from app.Models.events import Events
from venue.models.badges import BadgesLevel
from app.Models.challenge_achiever import Challenge_Achiever
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from django.db.models import Sum, Count, Q

# First one old 

# class EventBadgeProgressView(APIView):
#     permission_classes = [IsAuthenticated, Request_By_Customer_Only]

#     def post(self, request):

#         event_id = request.data.get('event')
#         data = []

#         event = Events.objects.filter(id=event_id).first()

#         user_joined_event = EventAttendees.objects.filter(
#             event=event,
#             user=request.user
#         ).first()
        
#         badge_levels = BadgesLevel.objects.filter(badge=event.badge)

#         participants_venues = VenuesParticipatingEvents.objects.filter(event=event)

#         if not user_joined_event:
#             return Response({"data":BadgesLevelSerializer(badge_levels, many=True).data, "message":"you haven't join this event, please join this event and achieve challenge to achieve this badge."})

        
#         if not participants_venues or participants_venues is None:
#             return Response({"data":BadgesLevelSerializer(badge_levels, many=True).data , "message":"This event do not have participating venues right now to scan and level up the badge."})


#         participants_venues_required_scans = {
#             v['venues']: v['scans_to_achieve_next_tier']
#             for v in participants_venues.values('venues','scans_to_achieve_next_tier')
#         }
        

#         participants_venues_scans_count = participants_venues.aggregate( 
#             total_scans_to_achieve_highest_level=Sum('scans_to_achieve_next_tier')
#         )

#         total_scans = participants_venues_scans_count.get(
#             'total_scans_to_achieve_highest_level'
#         ) or 0


#         badge_levels_count = badge_levels.count() if badge_levels.count() > 0 else 0

#         value_validate_on_each_level = (
#             floor(total_scans / badge_levels_count)
#             if badge_levels_count > 0 else 0
#         )


#         venue_ids = participants_venues.values_list('venues', flat=True)

#         challenges = Challenges.objects.filter(
#             venue__in=venue_ids
#         ) if participants_venues else None

        

#         # BASIC BADGE
#         badge_basic_level = badge_levels.filter(
#             category__category__icontains='basic'
#         ).first()

#         if badge_basic_level:
#             data.append({
#                 **BadgesLevelSerializer(badge_basic_level).data,
#                 'status': True,
#                 'message': "You have passed the basic level of this event"
#             })
#         else:
#             data.append({                  
#                 **BadgesLevelSerializer(badge_basic_level).data,
#                 'status': False,
#                 'message': "You didn't attend this event"
#             })


#         calculate_validation_time = 0

#         # Count once instead of inside loop
#         challenges_achieved = 0
#         user_scans = None
#         achieved_venues_count = 0
       
#         if challenges and user_joined_event:

#             start_date = max(user_joined_event.joined_at, user_joined_event.event.event_start_date)
#             end_date = user_joined_event.event.event_close_date
#             challenges_achieved_list = Challenge_Achiever.objects.filter(
#                 challenge__in=challenges,
#                 customer_taken=request.user,
#                 scanned_at__gte=start_date,
#                 scanned_at__lte=end_date
#             )
#             challenges_achieved = challenges_achieved_list.count()
#             user_scans = challenges_achieved_list.values(
#                 'challenge__venue'
#             ).annotate(
#                 total_scans=Count('id')
#             )
        
      
        
#         user_scans_dict = {
#             scan['challenge__venue']: scan['total_scans']
#             for scan in user_scans
#         } if user_scans is not None else {}
      

#         actual_scans_sum = sum(
#             min(user_scans_dict.get(k, 0), participants_venues_required_scans[k])
#             for k in participants_venues_required_scans
#         )       
        
   
#         for level in badge_levels:

#             if challenges and user_joined_event:
#                 remaining_scans = participants_venues_scans_count['total_scans_to_achieve_highest_level'] - actual_scans_sum
                
                
#                 calculate_validation_time += value_validate_on_each_level
           
#                 if actual_scans_sum >= calculate_validation_time:
#                     data.append({
#                         **BadgesLevelSerializer(level).data,
#                         'status': True,
#                         'message': f"You have passed the {level.category.category} level of this event"
#                     })
               
#                 else:
#                     data.append({
#                         **BadgesLevelSerializer(level).data,
#                         'status': False,
#                         'message': f"You’re {remaining_scans} scans away from completing this event"
#                     })
#             else:
#                 data.append({
#                     **BadgesLevelSerializer(level).data,
#                     'status': False,
#                     'message': "To achieve next level you need to join this event and complete the required tasks"
#                 })

#         return Response(data)



# Another Created

class EventBadgeProgressView(APIView):
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]

    def post(self, request):

        event_id = request.data.get('event')
     

        data = []

        event = Events.objects.filter(id=event_id).first()

        user_joined_event = EventAttendees.objects.filter(
            event=event,
            user=request.user
        ).first()
        
        badge_levels = BadgesLevel.objects.filter(badge=event.badge)

        participants_venues = VenuesParticipatingEvents.objects.filter(event=event)

        if not user_joined_event:
            return Response({"data":BadgesLevelSerializer(badge_levels, many=True).data, "message":"you haven't join this event, please join this event and achieve challenge to achieve this badge."})
        
        if not participants_venues or participants_venues is None:
            return Response({"data":BadgesLevelSerializer(badge_levels, many=True).data , "message":"This event do not have participating venues right now to scan and level up the badge."})


        participants_venues_required_scans = {
            v['venues']: v['scans_to_achieve_next_tier']
            for v in participants_venues.values('venues','scans_to_achieve_next_tier')
        }
        
        participants_venues_scans_count = participants_venues.aggregate( 
            total_scans_to_achieve_highest_level=Sum('scans_to_achieve_next_tier')
        )

        total_scans = participants_venues_scans_count.get(
            'total_scans_to_achieve_highest_level'
        ) or 0


        badge_levels_count = badge_levels.count() if badge_levels.count() > 0 else 0

        value_validate_on_each_level = (
            floor(total_scans / badge_levels_count)
            if badge_levels_count > 0 else 0
        )

        calculate_validation_time = 0

        # Count once instead of inside loop
        challenges_achieved = None
        user_scans = None
        
    
        venue_filters = Q()

        for venue in participants_venues:
            end_date = min(
                venue.event.event_close_date,
                venue.available_till
            ) if venue.available_till else venue.event.event_close_date

            venue_filters |= Q(
                challenge__venue=venue.venues,
                scanned_at__gte=venue.event.event_start_date,
                scanned_at__lte=end_date
            )

        challenges_achieved = Challenge_Achiever.objects.filter(
            venue_filters,
            customer_taken=request.user
        )
        print(challenges_achieved)
        if not challenges_achieved.exists():
            return Response({"data":BadgesLevelSerializer(badge_levels, many=True).data , "message":"You haven't scanned any challenges in this event yet, please scan challenges in this event to level up the badge."})
        
        user_scans = challenges_achieved.values(
            'challenge__venue'
        ).annotate(
            total_scans=Count('id')
        )

        challenges_achieved = challenges_achieved.count() if challenges_achieved is not None else 0
        
        user_scans_dict = {
            scan['challenge__venue']: scan['total_scans']
            for scan in user_scans
        } if user_scans is not None else {}
      

        actual_scans_sum = sum(
            min(user_scans_dict.get(k, 0), participants_venues_required_scans[k])
            for k in participants_venues_required_scans
        )       
        

        for level in badge_levels:
            
            if user_joined_event:
                remaining_scans = participants_venues_scans_count['total_scans_to_achieve_highest_level'] - actual_scans_sum
                calculate_validation_time += value_validate_on_each_level
           
                if actual_scans_sum >= calculate_validation_time:
                    data.append({
                        **BadgesLevelSerializer(level).data,
                        'status': True,
                        'message': f"You have passed the {level.category.category} level of this event"
                    })
               
                else:
                    data.append({
                        **BadgesLevelSerializer(level).data,
                        'status': False,
                        'message': f"You’re {remaining_scans} scans away from completing this event"
                    })
            else:
                data.append({
                    **BadgesLevelSerializer(level).data,
                    'status': False,
                    'message': "To achieve next level you need to join this event and complete the required tasks"
                })

        return Response(data)