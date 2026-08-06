from rest_framework import generics 
from app.Models.trails.trailRecord import TrailRecord
from app.Models.trails.trailStepsRecord import TrailStepRecord
from app.Serializers.trailSerializers.trailstep_serializer import TrailStepSerializerStaff
from app.Serializers.trailSerializers.trailrecord_serializer import TrailRecordSerializer
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.pagination import PageNumberPagination

from datetime import timedelta

from django.db.models import (
    Avg,
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    IntegerField,
    Q,
    Sum,
    Value,
)
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10        
    page_size_query_param = 'page_size'
    max_page_size = 50





# class TrailRecordStepsStaff(generics.ListAPIView):
#     permission_classes = [IsAuthenticated, Request_By_Admin_Only]
#     queryset = TrailRecord.objects.all()
#     serializer_class = TrailRecordSerializer
#     pagination_class = StandardResultsSetPagination

class TrailRecordStepsStaff(generics.ListAPIView):
    permission_classes = [
        IsAuthenticated,
        Request_By_Admin_Only,
    ]

    serializer_class = TrailRecordSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return (
            TrailRecord.objects
            .select_related(
                "user",
                "user__customer_profile",
                "trail",
                "trail__reward",
                "trail__badge",
            )
            .prefetch_related(
                "trail__steps",
                "step_records",
                "step_records__step",
            )
            .order_by("-started_at")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset()
        )

        # Remove ordering when this queryset is used as a subquery.
        trail_record_ids = (
            queryset
            .order_by()
            .values_list("id", flat=True)
        )

        step_records = TrailStepRecord.objects.filter(
            trail_record_id__in=trail_record_ids
        )

        # =========================================================
        # MAIN TRAIL-RECORD STATISTICS
        # =========================================================

        record_stats = queryset.order_by().aggregate(
            total_attempts=Count("id"),

            completed_attempts=Count(
                "id",
                filter=Q(
                    status=TrailRecord.Status.COMPLETED
                ),
            ),

            in_progress_attempts=Count(
                "id",
                filter=Q(
                    status=TrailRecord.Status.IN_PROGRESS
                ),
            ),

            abandoned_attempts=Count(
                "id",
                filter=Q(
                    status=TrailRecord.Status.ABANDONED
                ),
            ),

            unique_participants=Count(
                "user_id",
                distinct=True,
            ),

            rewards_awarded=Count(
                "id",
                filter=Q(reward_awarded=True),
            ),

            points_awarded_attempts=Count(
                "id",
                filter=Q(points_awarded__gt=0),
            ),

            total_points_awarded=Coalesce(
                Sum("points_awarded"),
                Value(0),
                output_field=IntegerField(),
            ),
        )

        total_attempts = record_stats["total_attempts"]
        completed_attempts = record_stats["completed_attempts"]
        unique_participants = record_stats["unique_participants"]

        distinct_trails_attempted = (
            queryset
            .order_by()
            .values("trail_id")
            .distinct()
            .count()
        )

        distinct_trails_completed = (
            queryset
            .filter(
                status=TrailRecord.Status.COMPLETED
            )
            .order_by()
            .values("trail_id")
            .distinct()
            .count()
        )

        repeat_participants = (
            queryset
            .order_by()
            .values("user_id")
            .annotate(
                attempts=Count("id")
            )
            .filter(attempts__gt=1)
            .count()
        )

        completion_rate = (
            round(
                completed_attempts / total_attempts * 100,
                2,
            )
            if total_attempts > 0
            else 0
        )

        average_attempts_per_user = (
            round(
                total_attempts / unique_participants,
                2,
            )
            if unique_participants > 0
            else 0
        )

        # =========================================================
        # SCAN AND FLAG STATISTICS
        # =========================================================

        verified_step_records = step_records.filter(
            qr_verified=True,
            completed=True,
        )

        total_verified_scans = (
            verified_step_records.count()
        )

        total_flagged_steps = (
            step_records
            .filter(flagged=True)
            .count()
        )

        flagged_record_ids = (
            step_records
            .filter(flagged=True)
            .order_by()
            .values_list(
                "trail_record_id",
                flat=True,
            )
            .distinct()
        )

        flagged_attempts = (
            flagged_record_ids.count()
        )

        pending_verification = (
            queryset
            .filter(
                id__in=flagged_record_ids,
                status=TrailRecord.Status.COMPLETED,
                reward_awarded=False,
                points_awarded=0,
            )
            .count()
        )

        flagged_attempt_rate = (
            round(
                flagged_attempts / total_attempts * 100,
                2,
            )
            if total_attempts > 0
            else 0
        )

        # =========================================================
        # AVERAGE COMPLETION TIME
        # =========================================================

        completion_duration = ExpressionWrapper(
            F("completed_at") - F("started_at"),
            output_field=DurationField(),
        )

        average_duration = (
            queryset
            .filter(
                status=TrailRecord.Status.COMPLETED,
                completed_at__isnull=False,
            )
            .aggregate(
                duration=Avg(completion_duration)
            )["duration"]
        )

        average_completion_minutes = (
            round(
                average_duration.total_seconds() / 60,
                2,
            )
            if average_duration
            else 0
        )

        # =========================================================
        # MOST SCANNED TRAILS
        # =========================================================

        raw_top_scanned_trails = list(
            verified_step_records
            .values(
                "trail_record__trail_id",
                "trail_record__trail__title",
            )
            .annotate(
                scan_count=Count("id"),
                unique_scanners=Count(
                    "trail_record__user_id",
                    distinct=True,
                ),
            )
            .order_by(
                "-scan_count",
                "trail_record__trail__title",
            )[:10]
        )

        top_scanned_trails = [
            {
                "trail_id": row[
                    "trail_record__trail_id"
                ],
                "trail_title": row[
                    "trail_record__trail__title"
                ],
                "scan_count": row["scan_count"],
                "unique_scanners": row[
                    "unique_scanners"
                ],
            }
            for row in raw_top_scanned_trails
        ]

        most_scanned_trail = (
            top_scanned_trails[0]
            if top_scanned_trails
            else None
        )

        # =========================================================
        # TRAIL PERFORMANCE
        # =========================================================

        raw_trail_performance = list(
            queryset
            .order_by()
            .values(
                "trail_id",
                "trail__title",
            )
            .annotate(
                attempts=Count("id"),

                completions=Count(
                    "id",
                    filter=Q(
                        status=TrailRecord.Status.COMPLETED
                    ),
                ),

                in_progress=Count(
                    "id",
                    filter=Q(
                        status=TrailRecord.Status.IN_PROGRESS
                    ),
                ),

                abandoned=Count(
                    "id",
                    filter=Q(
                        status=TrailRecord.Status.ABANDONED
                    ),
                ),
            )
            .order_by("-attempts")[:10]
        )

        performance_trail_ids = [
            row["trail_id"]
            for row in raw_trail_performance
        ]

        scan_count_rows = (
            verified_step_records
            .filter(
                trail_record__trail_id__in=(
                    performance_trail_ids
                )
            )
            .values(
                "trail_record__trail_id"
            )
            .annotate(
                scan_count=Count("id")
            )
        )

        scans_by_trail = {
            row["trail_record__trail_id"]: (
                row["scan_count"]
            )
            for row in scan_count_rows
        }

        trail_performance = []

        for row in raw_trail_performance:
            attempts = row["attempts"]
            completions = row["completions"]

            trail_performance.append({
                "trail_id": row["trail_id"],
                "trail_title": row["trail__title"],
                "attempts": attempts,
                "completions": completions,
                "in_progress": row["in_progress"],
                "abandoned": row["abandoned"],
                "scan_count": scans_by_trail.get(
                    row["trail_id"],
                    0,
                ),
                "completion_rate": (
                    round(
                        completions / attempts * 100,
                        2,
                    )
                    if attempts > 0
                    else 0
                ),
            })

        # =========================================================
        # DAILY ACTIVITY FOR THE LAST 30 DAYS
        # =========================================================

        today = timezone.localdate()
        activity_start = timezone.now() - timedelta(
            days=29
        )

        attempts_started_rows = (
            queryset
            .filter(
                started_at__gte=activity_start
            )
            .annotate(
                day=TruncDate("started_at")
            )
            .values("day")
            .annotate(
                count=Count("id")
            )
            .order_by("day")
        )

        trails_completed_rows = (
            queryset
            .filter(
                completed_at__gte=activity_start,
                status=TrailRecord.Status.COMPLETED,
            )
            .annotate(
                day=TruncDate("completed_at")
            )
            .values("day")
            .annotate(
                count=Count("id")
            )
            .order_by("day")
        )

        scans_rows = (
            verified_step_records
            .filter(
                completed_at__gte=activity_start
            )
            .annotate(
                day=TruncDate("completed_at")
            )
            .values("day")
            .annotate(
                count=Count("id")
            )
            .order_by("day")
        )

        attempts_started_map = {
            row["day"]: row["count"]
            for row in attempts_started_rows
        }

        trails_completed_map = {
            row["day"]: row["count"]
            for row in trails_completed_rows
        }

        scans_map = {
            row["day"]: row["count"]
            for row in scans_rows
        }

        activity_over_time = []

        for days_ago in range(29, -1, -1):
            day = today - timedelta(days=days_ago)

            activity_over_time.append({
                "date": day.isoformat(),
                "attempts_started": (
                    attempts_started_map.get(day, 0)
                ),
                "steps_scanned": scans_map.get(day, 0),
                "trails_completed": (
                    trails_completed_map.get(day, 0)
                ),
            })

        # =========================================================
        # STATUS AND AWARD CHART DATA
        # =========================================================

        status_breakdown = [
            {
                "status": "Completed",
                "count": completed_attempts,
            },
            {
                "status": "In progress",
                "count": record_stats[
                    "in_progress_attempts"
                ],
            },
            {
                "status": "Abandoned",
                "count": record_stats[
                    "abandoned_attempts"
                ],
            },
        ]

        physical_rewards = record_stats[
            "rewards_awarded"
        ]

        points_rewards = record_stats[
            "points_awarded_attempts"
        ]

        completed_without_award = max(
            completed_attempts
            - physical_rewards
            - points_rewards
            - pending_verification,
            0,
        )

        award_distribution = [
            {
                "type": "Physical reward",
                "count": physical_rewards,
            },
            {
                "type": "Points awarded",
                "count": points_rewards,
            },
            {
                "type": "Pending verification",
                "count": pending_verification,
            },
            {
                "type": "Completed without award",
                "count": completed_without_award,
            },
        ]

        dashboard = {
            "total_attempts": total_attempts,
            "distinct_trails_attempted": (
                distinct_trails_attempted
            ),
            "completed_attempts": completed_attempts,
            "distinct_trails_completed": (
                distinct_trails_completed
            ),
            "in_progress_attempts": record_stats[
                "in_progress_attempts"
            ],
            "abandoned_attempts": record_stats[
                "abandoned_attempts"
            ],
            "completion_rate": completion_rate,

            "total_verified_scans": (
                total_verified_scans
            ),
            "most_scanned_trail": (
                most_scanned_trail
            ),

            "flagged_attempts": flagged_attempts,
            "total_flagged_steps": (
                total_flagged_steps
            ),
            "flagged_attempt_rate": (
                flagged_attempt_rate
            ),
            "pending_verification": (
                pending_verification
            ),

            "unique_participants": (
                unique_participants
            ),
            "repeat_participants": (
                repeat_participants
            ),
            "average_attempts_per_user": (
                average_attempts_per_user
            ),

            "rewards_awarded": physical_rewards,
            "points_awarded_attempts": (
                points_rewards
            ),
            "total_points_awarded": record_stats[
                "total_points_awarded"
            ],

            "average_completion_minutes": (
                average_completion_minutes
            ),
        }

        charts = {
            "status_breakdown": status_breakdown,
            "activity_over_time": activity_over_time,
            "top_scanned_trails": top_scanned_trails,
            "trail_performance": trail_performance,
            "award_distribution": award_distribution,
        }

        # =========================================================
        # PAGINATED RESPONSE
        # =========================================================

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )

            response = self.get_paginated_response(
                serializer.data
            )

            response.data["trail_records"] = (
                response.data.pop("results")
            )

            response.data["dashboard"] = dashboard
            response.data["charts"] = charts

            return response

        # Same structure when pagination is unavailable.
        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response({
            "count": total_attempts,
            "next": None,
            "previous": None,
            "trail_records": serializer.data,
            "dashboard": dashboard,
            "charts": charts,
        })




