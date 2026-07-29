from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.trails.trailRecord import TrailRecord
from app.Models.trails.trailSteps import TrailStep
from app.Models.trails.trailStepsRecord import TrailStepRecord
from django.utils import timezone
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from math import radians, sin, cos, asin, sqrt







class UserTrailRecordSave(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def calculate_distance(
        self,
        user_latitude,
        user_longitude,
        step_latitude,
        step_longitude
    ):
        earth_radius_km = 6371

        user_latitude = radians(user_latitude)
        user_longitude = radians(user_longitude)
        step_latitude = radians(step_latitude)
        step_longitude = radians(step_longitude)

        latitude_difference = step_latitude - user_latitude
        longitude_difference = step_longitude - user_longitude

        value = (
            sin(latitude_difference / 2) ** 2
            + cos(user_latitude)
            * cos(step_latitude)
            * sin(longitude_difference / 2) ** 2
        )

        return 2 * earth_radius_km * asin(sqrt(value))

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user

        trail_code = str(
            request.data.get("code", "")
        ).strip()

        user_longitude = request.data.get("longitude")
        user_latitude = request.data.get("latitude")

        if not trail_code:
            return Response(
                {
                    "error": "QR code is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if user_longitude is None or user_latitude is None:
            return Response(
                {
                    "error": (
                        "The user's longitude and latitude "
                        "are required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_longitude = float(user_longitude)
            user_latitude = float(user_latitude)

        except (TypeError, ValueError):
            return Response(
                {
                    "error": (
                        "Longitude and latitude must be "
                        "valid numbers."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        trail_step = (
            TrailStep.objects
            .select_related(
                "trail",
                "trail__reward",
                "qr_code",
            )
            .filter(
                qr_code__code__iexact=trail_code
            )
            .first()
        )

        if trail_step is None:
            return Response(
                {
                    "error": "Invalid trail-step QR code."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        trail = trail_step.trail

        if not trail.is_active:
            return Response(
                {
                    "error": "Trail is not active."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get the user's current active attempt.
        trail_record = (
            TrailRecord.objects
            .select_for_update()
            .filter(
                user=user,
                trail=trail,
                status=TrailRecord.Status.IN_PROGRESS
            )
            .order_by("-attempt_number")
            .first()
        )

        new_attempt_created = False
        existing_step_record = None

        if trail_record is not None:
            existing_step_record = (
                TrailStepRecord.objects
                .filter(
                    trail_record=trail_record,
                    step=trail_step
                )
                .first()
            )

            # Return normally when this step was already completed.
            if (
                existing_step_record is not None
                and existing_step_record.completed
            ):
                return Response(
                    {
                        "message": (
                            "This step has already been completed "
                            "during the current attempt."
                        ),
                        "trail_record_id": trail_record.id,
                        "step_record_id": existing_step_record.id,
                        "attempt_number": (
                            trail_record.attempt_number
                        ),
                    },
                    status=status.HTTP_200_OK
                )

            # Get all completed steps for this attempt.
            completed_step_ids = (
                trail_record.step_records
                .filter(completed=True)
                .values_list("step_id", flat=True)
            )

            # The earliest incomplete step is the only allowed step.
            expected_step = (
                trail.steps
                .exclude(id__in=completed_step_ids)
                .order_by("order")
                .first()
            )

        else:
            # There is no active attempt, so only the first trail
            # step can start a new attempt.
            expected_step = (
                trail.steps
                .order_by("order")
                .first()
            )

        if expected_step is None:
            return Response(
                {
                    "error": "This trail does not contain any steps."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Reject a later step when an earlier step is incomplete.
        if trail_step.id != expected_step.id:
            return Response(
                {
                    "error": (
                        "Trail steps must be completed "
                        "in the correct order."
                    ),
                    "expected_step": {
                        "id": expected_step.id,
                        "title": expected_step.title,
                        "order": expected_step.order,
                    },
                    "scanned_step": {
                        "id": trail_step.id,
                        "title": trail_step.title,
                        "order": trail_step.order,
                    },
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create an attempt only after confirming that the user
        # scanned the correct step.
        if trail_record is None:
            latest_attempt_number = (
                TrailRecord.objects
                .filter(
                    user=user,
                    trail=trail
                )
                .aggregate(
                    maximum=Max("attempt_number")
                )["maximum"]
                or 0
            )

            trail_record = TrailRecord.objects.create(
                user=user,
                trail=trail,
                attempt_number=latest_attempt_number + 1,
                status=TrailRecord.Status.IN_PROGRESS
            )

            new_attempt_created = True

        distance = self.calculate_distance(
            user_latitude,
            user_longitude,
            float(trail_step.latitude),
            float(trail_step.longitude)
        )

        # calculate_distance() returns kilometres.
        # 0.05 kilometres equals 50 metres.
        outside_allowed_distance = distance > 0.05

        continued_on_another_day = (
            timezone.localtime(
                trail_record.started_at
            ).date()
            != timezone.localdate()
        )

        should_flag = (
            outside_allowed_distance
            or continued_on_another_day
        )

        if existing_step_record is None:
            step_record = TrailStepRecord.objects.create(
                trail_record=trail_record,
                step=trail_step,
                completed=True,
                flagged=should_flag,
                qr_verified=True,
            )

        else:
            step_record = existing_step_record
            step_record.completed = True
            step_record.qr_verified = True
            step_record.flagged = should_flag
            step_record.save()

        total_steps = trail.steps.count()

        completed_steps = (
            trail_record.step_records
            .filter(completed=True)
            .count()
        )

        flagged_steps = (
            trail_record.step_records
            .filter(flagged=True)
            .count()
        )

        trail_completed = (
            total_steps > 0
            and completed_steps >= total_steps
        )

        if trail_completed:
            trail_record.status = TrailRecord.Status.COMPLETED
            trail_record.completed_at = timezone.now()

            if trail.reward_id is not None:
                trail_record.reward_awarded = True
                trail_record.points_awarded = 0

            else:
                trail_record.reward_awarded = False
                trail_record.points_awarded = (
                    trail.reward_points
                )

            trail_record.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "reward_awarded",
                    "points_awarded",
                ]
            )

        progress_percentage = (
            round(
                completed_steps / total_steps * 100,
                2
            )
            if total_steps > 0
            else 0
        )

        next_step = trail_record.suggested_next_step

        return Response(
            {
                "message": (
                    "Trail completed successfully."
                    if trail_completed
                    else "Trail step saved successfully."
                ),
                "new_attempt_created": new_attempt_created,
                "trail_record": {
                    "id": trail_record.id,
                    "trail_id": trail.id,
                    "trail_title": trail.title,
                    "attempt_number": (
                        trail_record.attempt_number
                    ),
                    "status": trail_record.status,
                },
                "scanned_step": {
                    "id": trail_step.id,
                    "title": trail_step.title,
                    "order": trail_step.order,
                    "completed": step_record.completed,
                    "flagged": step_record.flagged,
                    "qr_verified": step_record.qr_verified,
                    "distance_km": round(distance, 4),
                },
                "progress": {
                    "total_steps": total_steps,
                    "completed_steps": completed_steps,
                    "flagged_steps": flagged_steps,
                    "percentage": progress_percentage,
                },
                "suggested_next_step": (
                    {
                        "id": next_step.id,
                        "title": next_step.title,
                        "order": next_step.order,
                        "latitude": next_step.latitude,
                        "longitude": next_step.longitude,
                    }
                    if next_step is not None
                    else None
                ),
            },
            status=(
                status.HTTP_201_CREATED
                if new_attempt_created
                else status.HTTP_200_OK
            )
        )






















# class UserTrialRecordSave(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
  
#     def post(self):
#         user = self.request.user
#         trail_code = self.request.data.get("code")
#         user_longitude = self.request.data.get("longitude")
#         user_latitude = self.request.data.get("latitude")
#         trail_step = TrailSteps.objects.filter(qr_code__code__iexact=trail_code).first()
#         trail = trail_step.trail

#         if not trail_step:
#             return Response(
#                 {"error": "Trail not found."},
#                 status=404
#             )
        
#         if trail.is_active == False:
#             return Response(
#                 {"error": "Trail is not active."},
#                 status=400
#             )

       
#         if not TrailRecord.objects.filter(user=user, trail=trail, status=TrailRecord.Status.IN_PROGRESS).exists():
#             trail_record = TrailRecord.objects.create(
#                 user=user,
#                 trail=trail,
#                 attempt_number=1,
#                 status=TrailRecord.Status.IN_PROGRESS
#             )
            
#             if not TrailStepRecord.objects.filter(trail_record=trail_record, step=trail_step).exists():
#                 if trail_step.latitude and trail_step.longitude:
#                     # Calculate the distance between the user's location and the trail step's location
#                     distance = self.calculate_distance(
#                         user_latitude, user_longitude,
#                         trail_step.latitude, trail_step.longitude
#                     )

#                     if distance <= 0.05:  # 50 meters
#                         trail_step_record = TrailStepRecord.objects.create(
#                             trail_record=trail_record,
#                             step=trail_step,
#                             completed=True,
#                             qr_verified=True,
#                             completed_at=timezone.now(),
#                         )
#                     elif not trail_record.started_at.date() == timezone.now().date():
#                         trail_step_record = TrailStepRecord.objects.create(
#                                 trail_record=trail_record,
#                                 step=trail_step,
#                                 completed=True,
#                                 flagged=True,
#                                 qr_verified=True,
#                                 flagged_at=timezone.now(),
#                             )
#                     else:
#                         trail_step_record = TrailStepRecord.objects.create(
#                             trail_record=trail_record,
#                             step=trail_step,
#                             completed=True,
#                             qr_verified=True,
#                             completed_at=timezone.now(),
#                         )
                                      

#         else:
#             return Response(
#                 {"error": "User has already completed this trail."},
#                 status=400
#             )
