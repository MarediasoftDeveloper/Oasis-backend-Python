# from math import floor

# from rest_framework import generics
# from rest_framework.views import APIView
# from app.models import Customer_profile
# from app.Permissions.send_by_customer_only import Request_By_Customer_Only
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework import status
# import calendar
# from rest_framework.exceptions import ValidationError
# from django.utils import timezone
# from app.Models.venues_participating_in_event import VenuesParticipatingEvents
# from app.Models.event_attendees import EventAttendees
# from venue.models.challenges import Challenges
# from app.Models.events import Events
# from venue.models.badges import BadgesLevel
# from app.Models.challenge_achiever import Challenge_Achiever
# from app.Serializers.badge_level_serializer import BadgesLevelSerializer
# from django.db.models import Sum, Count
# from staff.Permissions.adminOrganiserOnlyPermission import Request_By_Admin_And_Organiser_Only 


# class EventBadgeProgressStaffView(APIView):
#     permission_classes = [IsAuthenticated, Request_By_Admin_And_Organiser_Only]

#     def post(self, request):

#         event_id = request.data.get('event')
#         print('event_id', event_id)
#         user_id = request.data.get('user')
#         print('user_id', user_id)

#         if user_id is None:
#             return Response({"message": "User not found!"}, status=status.HTTP_400_BAD_REQUEST)

#         data = []

#         event = Events.objects.filter(id=event_id).first()
   
#         earned_badges_qs = EventBadgesEarned.objects.filter(
#             event=event,
#             user__id=user_id
#         ).first()

#         user_joined_event = EventAttendees.objects.filter(
#             event=event,
#             user__id=user_id
#         ).first()
        
#         badge_levels = BadgesLevel.objects.filter(badge=event.badge)

#         participants_venues = VenuesParticipatingEvents.objects.filter(event=event)

#         if not user_joined_event:
#             return Response({"data":BadgesLevelSerializer(badge_levels, many=True).data, "message":"User haven't join this event, They have to join this event and Scan challenge to achieve this badge."})

#         if not earned_badges_qs:
#             return Response({"data":BadgesLevelSerializer(badge_levels, many=True).data , "message":"User haven't attended this event, They have to attend this event and Scan challenges to achieve this badge."})
        
#         if not participants_venues:
#             return Response({"data":BadgesLevelSerializer(badge_levels, many=True).data , "message":"This event do not have participating venues right now to scan and level up the badge."})


#         participants_venues_required_scans = {
#             v['venues']: v['scans_to_achieve_next_tier']
#             for v in participants_venues.values('venues','scans_to_achieve_next_tier')
#         }
        

#         if participants_venues is None:
#             return Response({"message":"participating venues are not found!"})


#         participants_venues_scans_count = participants_venues.aggregate(
#             total_scans_to_achieve_highest_level=Sum('scans_to_achieve_next_tier')
#         )

#         total_scans = participants_venues_scans_count.get(
#             'total_scans_to_achieve_highest_level'
#         ) or 0


#         badge_levels_count = badge_levels.count() - 1 if badge_levels.count() > 0 else 0

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

#         if badge_basic_level and earned_badges_qs:
#             full_name = (
#                 f"{earned_badges_qs.user.first_name} {earned_badges_qs.user.last_name}"
#                 if earned_badges_qs.user.first_name
#                 else earned_badges_qs.user.username
#             )
#             data.append({
#                 **BadgesLevelSerializer(badge_basic_level).data,
#                 'status': True,
#                 'message': f"{full_name} have passed the basic level of this event"
#             })
#         else:
#             data.append({                  
#                 **BadgesLevelSerializer(badge_basic_level).data,
#                 'status': False,
#                 'message': "You didn't attend this event"
#             })

#         # OTHER BADGE LEVELS
#         badge_levels = badge_levels.exclude(category__category__icontains='basic')

#         calculate_validation_time = 0

#         # Count once instead of inside loop
#         challenges_achieved = 0
#         user_scans = None
#         achieved_venues_count = 0
       
#         if challenges and earned_badges_qs and user_joined_event:
#             start_date = max(user_joined_event.joined_at, user_joined_event.event.event_start_date)
#             end_date = user_joined_event.event.event_close_date
#             challenges_achieved_list = Challenge_Achiever.objects.filter(
#                 challenge__in=challenges,
#                 customer_taken__id=user_id,
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

#             if challenges and earned_badges_qs and user_joined_event:
#                 remaining_scans = participants_venues_scans_count['total_scans_to_achieve_highest_level'] - actual_scans_sum
#                 full_name = (
#                     f"{earned_badges_qs.user.first_name} {earned_badges_qs.user.last_name}"
#                     if earned_badges_qs.user.first_name
#                     else earned_badges_qs.user.username
#                 )
                
#                 calculate_validation_time += value_validate_on_each_level
           
#                 if actual_scans_sum >= calculate_validation_time:
#                     data.append({
#                         **BadgesLevelSerializer(level).data,
#                         'status': True,
#                         'message': f"{full_name} have passed the {level.category.category} level of this event"
#                     })
               
#                 else:
#                     data.append({
#                         **BadgesLevelSerializer(level).data,
#                         'status': False,
#                         'message': f"To pass this level {full_name} need to scan {remaining_scans} more challenges in this event"
#                     })
#             else:
#                 data.append({
#                     **BadgesLevelSerializer(level).data,
#                     'status': False,
#                     'message': f"To achieve next level {full_name} need to join this event and complete the required tasks"
#                 })

#         return Response(data)



