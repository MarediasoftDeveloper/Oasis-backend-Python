from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Serializers.earned_badges_by_user_serializer import Earned_Badges_By_User_Serializer
from rest_framework import status
from ..Models.earned_badges_by_user import Earned_Badges
from venue.models.badge_category import Badge_Category
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from django.utils import timezone
from datetime import datetime


class User_Badges_Record(APIView):

    permission_classes=[IsAuthenticated]

    def get(self, request, id):
        
        earned_badges = Earned_Badges.objects.filter(user=request.user, badge__id=id)
        badges_category = Badge_Category.objects.all()
        data=[]
        for category in badges_category:
            filtered_badges = earned_badges.filter(badge__category=category)
            if filtered_badges:
                       
                earned_count = filtered_badges.count()
                badge = filtered_badges.first()
                if category.num_of_task_to_achieve_badge > filtered_badges.count():
                    data.append({
                        'category':category.category,
                        'earned_badges':earned_count,
                        'badge':badge.badge.name,
                        'remaining_badges_to_pass_this_level': category.num_of_task_to_achieve_badge - filtered_badges.count()
                    })
                else:
                    data.append({
                        'category':category.category,
                        'earned_badges':earned_count,
                        'badge': badge.badge.name,
                        'message': f"you have passed this {category.category} level"
                    })
            else:
                data.append({
                    'category':category.category,
                    'badge': badge.badge.name,
                    'message': f"No Earned badges for this {category.category} level"
                })

        return Response(data)
            



        

