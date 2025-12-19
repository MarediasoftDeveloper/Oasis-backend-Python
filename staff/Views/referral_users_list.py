# Create your views here.
from rest_framework.filters import SearchFilter 
from rest_framework import status, generics, filters
from rest_framework.response import Response
from app.Models.referrals_Users import ReferralsUsers
from app.Models.referrals import Referrals
from app.Serializers.referral_users_serializer import ReferralSerializer
from app.Serializers.referral_code_invite import Referral_Code_Serializer
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
import datetime
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20         
    page_size_query_param = 'page_size'
    max_page_size = 50


class ReferralUsersList(generics.ListAPIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    queryset = ReferralsUsers.objects.all().order_by('-id')
    serializer_class = ReferralSerializer

    def list(self, request, *args, **kwargs):
        today = timezone.now().date()

        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Base queryset
        queryset = self.filter_queryset(self.get_queryset())

        # Pagination
        paginator = self.pagination_class()
        paginated_referrals = paginator.paginate_queryset(queryset, request)

        # Weekly referrals
        weekly_used_referrals = queryset.filter(
            used_at__date__range=(start_of_week, end_of_week)
        )

        weekly_most_used_referral = (
            weekly_used_referrals
            .values("referral")
            .annotate(cnt=Count("id"))
            .order_by("-cnt")
            .first()
        )

        referral_obj = Referrals.objects.filter(id=int(weekly_most_used_referral['referral'])).first()

        if referral_obj:
            weekly_most_used_referral['referralDetials'] = Referral_Code_Serializer(referral_obj).data
        
        points_issued_by_referrals_this_week = (
            weekly_used_referrals.aggregate(
                total_points=Sum('points_issued')
            )['total_points'] or 0
        )

        serializer = self.get_serializer(paginated_referrals, many=True)

        return paginator.get_paginated_response({
            "referral_data": serializer.data,
            "total_referrals": queryset.count(),
            "weekly_referrals": weekly_used_referrals.count(),
            "most_used_referral": weekly_most_used_referral,
            "referral_points_this_week": points_issued_by_referrals_this_week,
        })