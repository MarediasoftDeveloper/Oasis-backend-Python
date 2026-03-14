from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.events import Events
from app.Serializers.earned_badges_by_user_serializer import Earned_Badges_By_User_Serializer
from rest_framework import status
from app.Models.event_badges_earned import EventBadgesEarned
from app.Models.venues_participating_in_event import VenuesParticipatingEvents
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from venue.models.badges import BadgesLevel, Badges
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from django.utils import timezone
import math
from django.db.models.functions import Lower


def validate_earned_badges(user, event):
    participating_venues = VenuesParticipatingEvents.objects.filter(event=event)
    

    return 

class UserEventBadgesRecord(APIView):

    permission_classes=[IsAuthenticated]

    def get(self, request, id):
        
        earned_badge = EventBadgesEarned.objects.filter(user=request.user, event__badge__id=id).first()    
        event = earned_badge.event if earned_badge else None
        venues = None
        if event is not None:
            venues = VenuesParticipatingEvents.objects.filter(event=event)

        badges_category = BadgesLevel.objects.filter(badge__id=id).order_by('points_per_task')
        filtered_badges=None
        data=[]
        earned_count=0
        for category in badges_category:
            if earned_badge:
                filtered_badges = EventBadgesEarned.objects.filter(user=request.user, event__badge=earned_badge.badge)  
            if filtered_badges:
                earned_count = filtered_badges.count()       
                f_badge = filtered_badges.first()
                
                if category.category.num_of_task_to_achieve_badge <= earned_count:
                    data.append({
                        **BadgesLevelSerializer(category).data,
                        'status':True,
                        'message': f"you have passed this {category.category.category} level"
                    })
                else:
                    data.append({
                        **BadgesLevelSerializer(category).data,
                        'status':False,
                        'remaining_badges_to_pass_this_level': category.category.num_of_task_to_achieve_badge - earned_count
                    })
            else:
                data.append({
                    **BadgesLevelSerializer(category).data,
                    'status':False,
                    'message': f"no earned badges for this {category.category.category} level"
                })
                        
        data.append({'earned_badges':earned_count, 'venues':venues})
      
        return Response(data)
            



        

