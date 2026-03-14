
# Create your views here.
from rest_framework.views import APIView
from rest_framework import status, generics, filters
from rest_framework.response import Response
from venue.Serializers.venue_info_serializer import VenueInfoSerializer
from app.Serializers.challenge_achiever_serializer import GetChallengeAchieverSerializer
from app.Serializers.rewards_achiever_serializer import GetRewardsAchievmentsSerializer
from staff.Serializers.raffles_entry_serializer_staff import GetRafflesEntrySerializerStaff
from app.Models.posts import Post
from app.models import Customer_profile, Customer
from app.Serializers.customer_profile_serializer import CustomerProfileSerializerStaff
from app.Serializers.post_serializer import PostSerializer
from app.Models.challenge_achiever import Challenge_Achiever
from app.Models.earned_badges_by_user import Earned_Badges
from app.Models.rewards_achiever import Rewards_Achiever
from app.Models.raffles_entry import Raffles_Entry
from app.Models.earned_badges_by_user import Earned_Badges
from app.Models.users_interests import User_Interest
from app.Serializers.users_interests_serializer import UserInterestSerializerStaff
from venue.models.venue_badges import Venue_Badges
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Count
from django.db.models import Count, Sum, OuterRef, Subquery, Prefetch
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from app.Views.utils.fcm import send_push_notification
from django.db import transaction

def format_number_ui(value):
    value = float(value)

    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return str(int(value)) if value.is_integer() else f"{value:.2f}"

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20         
    page_size_query_param = 'page_size'
    max_page_size = 50

class UsersDataAPI(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    serializer_class = CustomerProfileSerializerStaff
    search_fields = ['customer__username', 'customer__email','customer__first_name', 'customer__last_name']

    def get_queryset(self):

        total_scans_subquery = Challenge_Achiever.objects.filter(
            customer_taken=OuterRef('customer')
        ).values('customer_taken').annotate(
            total=Count('id')
        ).values('total')

        badges_subquery = Earned_Badges.objects.filter(
            user=OuterRef('customer'),
        ).values('user').annotate(
            total=Count('id')
        ).values('total')
    
        return (
            Customer_profile.objects
            .select_related('customer')
            .annotate(
                total_scans=Subquery(total_scans_subquery),
                total_badges=Subquery(badges_subquery),
            )
            .order_by('-customer__date_joined')
        )
        
    def list(self, request, *args, **kwargs):
        # THIS LINE FIXES SEARCH
        queryObj = self.get_queryset()
        queryset = self.filter_queryset(queryObj)
        paginator = self.pagination_class()
        paginated_customers = paginator.paginate_queryset(queryset, request)
        
        badges_earned = Earned_Badges.objects.all().count()
       
        points_in_circulation = Customer_profile.objects.all().aggregate(circulation_points=Sum('total_redeemed_points'))
        logged_in_users = OutstandingToken.objects.filter(
            expires_at__gte=timezone.now(), user__user_role='1'
        ).values("user_id").distinct().count()

        users_data={
            'total_users':Customer.objects.filter(user_role='1').count(),
            'badges_earned':badges_earned,
            'logged_in_users':logged_in_users,
            "points_in_millions": points_in_circulation['circulation_points'],
        }

        data = []

        for user in paginated_customers:
            serialized_user = CustomerProfileSerializerStaff(user).data

            serialized_user['total_scans'] = user.total_scans or 0
            serialized_user['total_badges'] = user.total_badges or 0
            serialized_user['joined_at'] = user.customer.date_joined
            serialized_user['logged_in'] = OutstandingToken.objects.filter(
            expires_at__gte=timezone.now(),
            user=user.customer
            ).exists()

            data.append(serialized_user)

        data.append(users_data)
        return paginator.get_paginated_response(data)
    

class UserRetrieveAPI(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    serializer_class = CustomerProfileSerializerStaff
    lookup_field='customer_id'

    def get_queryset(self):

        total_scans_subquery = Challenge_Achiever.objects.filter(
            customer_taken=OuterRef('customer')
        ).values('customer_taken').annotate(
            total=Count('id')
        ).values('total')

        badges_subquery = Earned_Badges.objects.filter(
            user=OuterRef('customer'),
        ).values('user').annotate(
            total=Count('id')
        ).values('total')
    
        return (
            Customer_profile.objects
            .select_related('customer')
            .annotate(
                total_scans=Subquery(total_scans_subquery),
                total_badges=Subquery(badges_subquery),
            )
            .order_by('-customer__date_joined')
        )
    

    def retrieve(self, request, *args, **kwargs):
        customer = self.get_object()
        posts = Post.objects.filter(user=customer.customer)
        #  Last 5 scans
        recent_scans = Challenge_Achiever.objects.filter(
            customer_taken=customer.customer
        ).order_by('-scanned_at')

        #  Last 5 rewards
        recent_rewards = Rewards_Achiever.objects.filter(
            customer_taken=customer.customer
        ).order_by('-achieved_at')

        #  Last 5 raffles
        recent_raffles = Raffles_Entry.objects.filter(
            user=customer.customer
        ).order_by('-joined_at')

        data = CustomerProfileSerializerStaff(customer).data
        
        # Attach computed values safely
        data['total_scans'] = customer.total_scans or 0
        data['total_badges'] = customer.total_badges or 0
        data['joined_at'] = customer.customer.date_joined

        data['posts'] = PostSerializer(posts, many=True).data
        #  Attach related activity
        data['customer_scans'] = GetChallengeAchieverSerializer(
            recent_scans, many=True
        ).data

        data['customer_rewards_achieved'] = GetRewardsAchievmentsSerializer(
            recent_rewards, many=True
        ).data

        data['customer_raffles_activity'] = GetRafflesEntrySerializerStaff(
            recent_raffles, many=True
        ).data

        data['scan_dict'] = {
            "count": recent_scans.count(),
            "total_win_points": recent_scans.aggregate(
                total_win_points=Sum("points_issued")
            )["total_win_points"] or 0
        }

        data['rewards_dict'] = {"count":recent_rewards.count(), "total_spent_points": recent_rewards.aggregate(
                total_spent_points=Sum("reward__required_points_for_reward")
            )["total_spent_points"] or 0}
        
        data['raffles_dict'] = {"count":recent_raffles.count(), "total_spent_points": recent_raffles.aggregate(
                total_spent_points=Sum("raffle__points_to_join")
            )["total_spent_points"] or 0, "total_win_points": recent_raffles.aggregate(
                total_rewarded_points=Sum("raffle__rewarded_points")
            )["total_rewarded_points"] or 0}

        return Response(data)




class UserUpdateDestroyAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    queryset = Customer_profile.objects.all()
    serializer_class = CustomerProfileSerializerStaff
    lookup_field='customer_id'

    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()

        with transaction.atomic():
            profile.customer.delete()

        return Response(
            {"message": "User deleted successfully"},
            status=status.HTTP_200_OK
        )


class SendNotificationToUser(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]

    def post(self, request):
        user = request.data.get('user_id')
        title = request.data.get('title')
        description = request.data.get('description')
        customer = Customer.objects.filter(id=user).first()
        result = send_push_notification(
            customer,
            title,
            description
        )
        return Response({"message":"Notificaiton have been sent successfully"})








class AdjustPointsOfUser(APIView):

    permission_classes = [IsAuthenticated, Request_By_Admin_Only]  # add admin-only if required

    def post(self, request):
        user_id = request.data.get('user_id')
        points = request.data.get('points')
        add_or_remove = request.data.get('add_or_remove')

        #  Basic validation
        if not user_id or not points or not add_or_remove:
            return Response(
                {"message": "user_id, points and add_or_remove are required"},
                status=400
            )

        try:
            points = int(points)
            if points <= 0:
                return Response(
                    {"message": "Points must be greater than 0"},
                    status=400
                )
        except ValueError:
            return Response(
                {"message": "Points must be a valid integer"},
                status=400
            )

        profile = Customer_profile.objects.filter(customer__id=user_id).first()

        if not profile:
            return Response(
                {"message": "Customer profile not found"},
                status=404
            )

        #  Atomic update
        with transaction.atomic():
            if add_or_remove == 'add':
                profile.total_redeemed_points += points

            elif add_or_remove == 'remove':
                if profile.total_redeemed_points < points:
                    return Response(
                        {"message": "Insufficient points to remove"},
                        status=400
                    )
                profile.total_redeemed_points -= points

            else:
                return Response(
                    {"message": "add_or_remove must be 'add' or 'remove'"},
                    status=400
                )

            profile.save()

        return Response({
            "message": "Points updated successfully",
            "user_id": user_id,
            "total_redeemed_points": profile.total_redeemed_points
        }, status=200)





class UserInterestsStaff(APIView):

    permission_classes = [IsAuthenticated, Request_By_Admin_Only]  # add admin-only if required

    def get(self, request, pk):
        user_interests = User_Interest.objects.filter(user__id=pk)
        serialized = UserInterestSerializerStaff(user_interests, many=True)
        return Response({"interests": serialized.data})
    