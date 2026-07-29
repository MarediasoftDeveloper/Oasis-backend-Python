from unicodedata import category

from rest_framework.views import APIView
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
from math import ceil, radians, sin, cos, asin, sqrt
from django.db.models import Prefetch
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from app.Serializers.trailSerializers.trailstep_serializer import TrailStepSerializer
from venue.models.badges import BadgesLevel




class GetUserTrailRecord(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, trail_id):
        user = request.user

        # Get the user's latest attempt for this trail.
        trail_record = (
            TrailRecord.objects
            .filter(
                user=user,
                trail_id=trail_id
            )
            .select_related(
                "user",
                "trail",
                "trail__reward",
                "trail__badge",
            )
            .prefetch_related(
                Prefetch(
                    "trail__steps",
                    queryset=TrailStep.objects
                    .select_related("qr_code")
                    .order_by("order")
                ),
                Prefetch(
                    "step_records",
                    queryset=TrailStepRecord.objects
                    .select_related("step")
                ),
                Prefetch(
                    "trail__badge__levels",
                    queryset=BadgesLevel.objects
                    .select_related("category")
                    .order_by("category_id", "id")
                ),
            )
            .order_by("-attempt_number")
            .first()
        )

        if trail_record is None:
            return Response(
                {
                    "detail": (
                        "No trail record was found for this "
                        "user and trail."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        trail = trail_record.trail

        # ---------------------------------------------------------
        # STEP DATA
        # ---------------------------------------------------------

        # Create a dictionary using the step ID.
        #
        # Example:
        # {
        #     1: TrailStepRecord(...),
        #     2: TrailStepRecord(...)
        # }
        step_record_map = {
            record.step_id: record
            for record in trail_record.step_records.all()
        }

        step_data = []

        # Iterate through all trail steps, including incomplete steps.
        for step in trail.steps.all():
            step_record = step_record_map.get(step.id)

            step_data.append({
                "step_id": step.id,
                "title": step.title,
                "description": step.description,
                "featured_image": (
                    request.build_absolute_uri(
                        step.featured_image.url
                    )
                    if step.featured_image
                    else None
                ),
                "pin_image": (
                    request.build_absolute_uri(
                        step.pin_image.url
                    )
                    if step.pin_image
                    else None
                ),
                "latitude": step.latitude,
                "longitude": step.longitude,
                "order": step.order,

                # When no TrailStepRecord exists, the step
                # has not been completed.
                "completed": (
                    step_record.completed
                    if step_record
                    else False
                ),
                "flagged": (
                    step_record.flagged
                    if step_record
                    else False
                ),
                "qr_verified": (
                    step_record.qr_verified
                    if step_record
                    else False
                ),
                "completed_at": (
                    step_record.completed_at
                    if step_record
                    else None
                ),
                "flagged_at": (
                    step_record.flagged_at
                    if step_record
                    else None
                ),
            })

        # ---------------------------------------------------------
        # BADGE LEVEL DATA
        # ---------------------------------------------------------

        badge_data = []

        if trail.badge_id is not None:
            badge_levels = list(
                trail.badge.levels.all()
            )

            completed_steps = (
                trail_record.completed_steps_count
            )

            total_steps = trail_record.total_steps

            # The TrailRecord.badge_level property returns
            # a level between 0 and 5.
            current_badge_level = (
                trail_record.badge_level
            )

            for index, badge_level in enumerate(
                badge_levels,
                start=1
            ):
                category_name = (
                    badge_level.category.category
                )

                level_passed = (
                    index <= current_badge_level
                )

                # The TrailRecord model divides progress
                # into exactly five badge levels.
                required_steps = (
                    ceil(index * total_steps / 5)
                    if total_steps > 0
                    else 0
                )

                remaining_steps = max(
                    required_steps - completed_steps,
                    0
                )

                serialized_badge = (
                    BadgesLevelSerializer(
                        badge_level,
                        context={
                            "request": request
                        }
                    ).data
                )

                badge_item = {
                    "level": index,
                    "badge": serialized_badge,
                    "status": level_passed,
                    "required_steps": required_steps,
                }

                if level_passed:
                    badge_item["message"] = (
                        f"You have passed the "
                        f"{category_name} level."
                    )
                else:
                    badge_item[
                        "remaining_steps_to_pass_this_level"
                    ] = remaining_steps

                    badge_item["message"] = (
                        f"Complete {remaining_steps} more "
                        f"step(s) to pass the "
                        f"{category_name} level."
                    )

                badge_data.append(badge_item)

        # ---------------------------------------------------------
        # SUGGESTED NEXT STEP
        # ---------------------------------------------------------

        suggested_next_step = (
            trail_record.suggested_next_step
        )

        suggested_next_step_data = None

        if suggested_next_step is not None:
            suggested_next_step_data = {
                "id": suggested_next_step.id,
                "title": suggested_next_step.title,
                "description": (
                    suggested_next_step.description
                ),
                "order": suggested_next_step.order,
                "latitude": suggested_next_step.latitude,
                "longitude": suggested_next_step.longitude,
                "featured_image": (
                    request.build_absolute_uri(
                        suggested_next_step
                        .featured_image.url
                    )
                    if suggested_next_step.featured_image
                    else None
                ),
                "pin_image": (
                    request.build_absolute_uri(
                        suggested_next_step.pin_image.url
                    )
                    if suggested_next_step.pin_image
                    else None
                ),
            }

        response_data = {
            "trail_record_id": trail_record.id,
            "user_id": user.id,
            "trail_id": trail.id,
            "trail_title": trail.title,
            "attempt_number": (
                trail_record.attempt_number
            ),
            "status": trail_record.status,
            "status_display": (
                trail_record.get_status_display()
            ),
            "started": trail_record.started,
            "completed": trail_record.completed,
            "flagged": trail_record.flagged,
            "started_at": trail_record.started_at,
            "completed_at": trail_record.completed_at,
            "points_awarded": (
                trail_record.points_awarded
            ),
            "reward_awarded": (
                trail_record.reward_awarded
            ),

            # Numeric current badge level.
            "badge_level": trail_record.badge_level,

            # Detailed list of all badge levels.
            "badge_levels": badge_data,

            "completed_steps_count": (
                trail_record.completed_steps_count
            ),
            "total_steps": trail_record.total_steps,
            "progress_percentage": (
                trail_record.progress_percentage
            ),
            "suggested_next_step": (
                suggested_next_step_data
            ),
            "steps": step_data,
        }

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )





# class GetUserTrailRecord(APIView):
#     permission_classes = [IsAuthenticated]


#     def get(self, request, trail_id):       
#         user = request.user
#         try:
#             trail_record = TrailRecord.objects.filter(
#                 user=user,
#                 trail_id=trail_id
#             ).order_by('-attempt_number').first()

#             if not trail_record:
#                 return Response(
#                     {"detail": "No trail record found for this user and trail."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             step_records = TrailStepRecord.objects.filter(
#                 trail_record=trail_record
#             ).select_related('step')

#             badge_levels = trail_record.trail.badge.levels.all()
#             badge_data = []
#             for index, badge_level in enumerate(
#                 badge_levels,
#                 start=1
#             ):
#                 if index <= trail_record.badge_level:
#                     badge_data.append({
#                         "badge": BadgesLevelSerializer(badge_level).data,
#                         "status": True,
#                         'message': f"you have passed this {category.category.category} level"
#                     })
#                 else:
#                     badge_data.append({
#                         "badge": BadgesLevelSerializer(badge_level).data,
#                         "status": False,
#                         'remaining_badges_to_pass_this_level': category.num_of_task_to_achieve_badge - trail_record.completed_steps_count
#                     })
    
                     
#             step_data = [
#                 {
#                     "step_id": step_record.step.id,
#                     "title": step_record.step.title,
#                     "description": step_record.step.description,
#                     "completed": step_record.completed,
#                     "flagged": step_record.flagged,
#                     "qr_verified": step_record.qr_verified,
#                     "completed_at": step_record.completed_at,
#                     "flagged_at": step_record.flagged_at
#                 }
#                 for step_record in step_records
#             ]

#             response_data = {
#                 "trail_record_id": trail_record.id,
#                 "user_id": user.id,
#                 "trail_id": trail_id,
#                 "attempt_number": trail_record.attempt_number,
#                 "status": trail_record.status,
#                 "flagged": trail_record.flagged,
#                 "started_at": trail_record.started_at,
#                 "completed_at": trail_record.completed_at,
#                 "points_awarded": trail_record.points_awarded,
#                 "reward_awarded": trail_record.reward_awarded,
#                 "badge_level": badge_data,
#                 "completed_steps_count": trail_record.completed_steps_count,
#                 "total_steps": trail_record.total_steps,
#                 "progress_percentage": trail_record.progress_percentage,
#                 # "suggested_next_step": TrailStepSerializer(trail_record.suggested_next_step).data if trail_record.suggested_next_step else None,
#                 "steps": step_data
#             }

#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"detail": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )