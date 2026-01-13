from rest_framework import generics
from app.Models.referrals import Referrals
from app.Models.referrals_Users import ReferralsUsers
from app.Models.posts import Post
from app.Serializers.referral_code_invite import Referral_Code_Serializer
from app.Serializers.referral_users_serializer import ReferralSerializer
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20         
    page_size_query_param = 'page_size'
    max_page_size = 50

class ReferralsList(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    serializer_class =ReferralSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return ReferralsUsers.objects.all().order_by('-id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        
        total_referrals = Referrals.objects.count()
        now = timezone.now()

        # Start of current week (Monday)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # End of current week (Sunday)
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

        week_referrals = queryset.filter(
            used_at__range=(start_of_week, end_of_week)
        ).order_by('-used_at')

        total_points_exchange = queryset.aggregate(
            total_points=Sum('points_issued')
        )['total_points'] or 0
        
        most_used_referral = (
            week_referrals
            .values('referral__id', 'referral__referral_code')
            .annotate(usage_count=Count('referral__id'))
            .order_by('-usage_count')
            .first()
        )
        print(most_used_referral)
        top_referrer =  (
            Referrals.objects.filter(id=most_used_referral['referral__id']).first()
            if most_used_referral
            else None
        )


        return self.get_paginated_response({
            "referrals_used": serializer.data,
            "total_referrals": total_referrals,
            "weekly_referrals_count": week_referrals.count(),
            "total_points_exchange": total_points_exchange,
            "top_referrer": Referral_Code_Serializer(top_referrer).data if top_referrer else None,
            "top_referrer_usage": most_used_referral['usage_count'] if top_referrer else None,
        })
