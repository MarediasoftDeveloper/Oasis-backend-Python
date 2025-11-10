from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Serializers.earned_badges_by_user_serializer import Earned_Badges_By_User_Serializer
from rest_framework import status
from ..Models.earned_badges_by_user import Earned_Badges
from venue.Serializers.badges_serializer import BadgesSerializer
from venue.models.badge_category import Badge_Category
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from django.utils import timezone
from datetime import datetime
from django.db.models.functions import Lower

class User_Badges_Record(APIView):

    permission_classes=[IsAuthenticated]

    def get(self, request, id):
        
       
        earned_badge = Earned_Badges.objects.filter(user=request.user, badge__id=id).first()
        if not earned_badge:
         raise serializers.ValidationError({
                "error": "This badge is not available!"
            })
        badges_category = Badge_Category.objects.all()
        data=[]
        for category in badges_category:
            filtered_badges = Earned_Badges.objects.filter(user=request.user, badge__name__iexact=earned_badge.badge.name.lower(), badge__category=category)
            if filtered_badges:
                earned_count = filtered_badges.count()       
                f_badge = filtered_badges.first()
                if category.num_of_task_to_achieve_badge > earned_count:
                    data.append({
                        "category":category.category,
                        **Earned_Badges_By_User_Serializer(f_badge).data,
                        'earned_badges':earned_count,
                        'remaining_badges_to_pass_this_level': category.num_of_task_to_achieve_badge - earned_count
                    })
                else:
                    data.append({
                        "category":category.category,
                        **Earned_Badges_By_User_Serializer(f_badge).data,
                        'earned_badges':earned_count,
                        'message': f"you have passed this {category.category} level"
                    })
            else:
                data.append({
                    'category':category.category,
                    'badge': BadgesSerializer(f_badge.badge).data,
                    'message': f"No Earned badges for this {category.category} level"
                })
      

        return Response(data)
            



        

