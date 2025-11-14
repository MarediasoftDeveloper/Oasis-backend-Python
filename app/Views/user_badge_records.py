from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Serializers.earned_badges_by_user_serializer import Earned_Badges_By_User_Serializer
from rest_framework import status
from ..Models.earned_badges_by_user import Earned_Badges
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from venue.models.badges import BadgesLevel, Badges
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from django.utils import timezone
from datetime import datetime
import math
from django.db.models.functions import Lower


class User_Badges_Record(APIView):

    permission_classes=[IsAuthenticated]

    def get(self, request, id):
        
       
        earned_badge = Earned_Badges.objects.filter(user=request.user, badge__id=id).first()    
        print(earned_badge)
        if not earned_badge:
         raise serializers.ValidationError({
                "error": "This badge is not available!"
            })
        badges_category = BadgesLevel.objects.filter(badge__id=id)
        data=[]
        earned_count=0
        for category in badges_category:
            filtered_badges = Earned_Badges.objects.filter(user=request.user, badge=earned_badge.badge)
            if filtered_badges:
                earned_count = filtered_badges.count() | 0       
                f_badge = filtered_badges.first()
                
                if category.category.num_of_task_to_achieve_badge < earned_count:
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
                    'message': f"No Earned badges for this {category.category.category} level"
                })
                        
        data.append({'earned_badges':earned_count})
      
        return Response(data)
            



        

