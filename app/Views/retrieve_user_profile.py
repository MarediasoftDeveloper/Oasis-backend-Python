from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.models import Customer_profile, Customer
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from app.Models.posts import Post
from app.Serializers.post_serializer import PostSerializer
from app.Models.friendships import Friendships
from app.Models.earned_badges_by_user import Earned_Badges
from django.db.models import Q

class Retrieve_User_Profile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        user_info= Customer_profile.objects.get(customer__id=id)
        earned_badges= Earned_Badges.objects.filter(user__id=id).count()
        serialized_posts =None
        friendship_status =None
        if not user_info.is_private:
            posts= Post.objects.filter(user__id=id)
            posts = PostSerializer(posts, many=True).data
        else:
            posts="This is a private account you can't see the posts of this user!"
        posts_count= Post.objects.filter(user__id=id).count()
        user_profile = CustomerProfileSerializer(user_info)
        friends = Friendships.objects.filter(Q(request_sender=user_info.customer) | Q(request_getter=user_info.customer))
        is_friend_obj = Friendships.objects.filter(Q(request_sender=user_info.customer, request_getter=self.request.user) | Q(request_sender=self.request.user, request_getter=user_info.customer)).first()
        if is_friend_obj and is_friend_obj.status=='accepted':
            friendship_status = {'status':True}
        elif is_friend_obj and is_friend_obj.status=='pending' and is_friend_obj.request_sender==self.request.user:
            friendship_status = {
                'request_send':True,
                "status":is_friend_obj.status,
            }
        elif is_friend_obj and is_friend_obj.status=='pending' and is_friend_obj.request_getter==self.request.user:
            friendship_status = {
                'request_send':False,
                "status":is_friend_obj.status,
            }
        else:
            friendship_status={'status':False}

        friends = friends.filter(status='accepted').count()
        return Response({
            **user_profile.data,
            'friends': friends,
            'badges': earned_badges,
            'posts_count': posts_count,
            'friendship_status':friendship_status,
            'posts': posts,
            })
