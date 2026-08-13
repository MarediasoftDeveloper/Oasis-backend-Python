from decimal import ROUND_HALF_UP, Decimal

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.trails.trailRecord import TrailRecord
from app.Models.trails.trailSteps import TrailStep
from app.Models.rewards_achiever import Rewards_Achiever
from app.Models.earned_points import Earned_Points
from app.Models.trails.trailStepsRecord import TrailStepRecord
from django.utils import timezone
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from math import radians, sin, cos, asin, sqrt
from math import ceil
from app.Serializers.badge_level_serializer import BadgesLevelSerializer

@transaction.atomic
def AssignRewardtoUser(trail, user):
    if trail.reward is not None:
        # Assign the reward to the user
        reward_assigned = Rewards_Achiever.objects.create(
            customer_taken=user,
            reward=trail.reward
        )
        return True

    return False

@transaction.atomic
def AssignPointstoUser(trail, user):
    if trail.reward_points is not None and trail.reward_points > 0:
        # Assign points to the user
        user_profile = user.customer_profile
        user_profile.total_redeemed_points += trail.reward_points
        user_profile.save()
        points_earned = Earned_Points.objects.create(
            customer=user,
            points_earned=trail.reward_points
        )
        return True

    return False
    


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

        latitude_difference = (
            step_latitude - user_latitude
        )

        longitude_difference = (
            step_longitude - user_longitude
        )

        value = (
            sin(latitude_difference / 2) ** 2
            + cos(user_latitude)
            * cos(step_latitude)
            * sin(longitude_difference / 2) ** 2
        )

        return (
            2
            * earth_radius_km
            * asin(sqrt(value))
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user

        trail_code = str(
            request.data.get("code", "")
        ).strip()

        user_longitude = request.data.get(
            "longitude"
        )

        user_latitude = request.data.get(
            "latitude"
        )

        # --------------------------------------------------
        # Validate QR code
        # --------------------------------------------------

        if not trail_code:
            return Response(
                {
                    "error": "QR code is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # --------------------------------------------------
        # Validate GPS coordinates
        # --------------------------------------------------

        if (
            user_longitude is None
            or user_latitude is None
        ):
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
            user_longitude = Decimal(
                str(user_longitude)
            ).quantize(
                Decimal("0.000001"),
                rounding=ROUND_HALF_UP
            )

            user_latitude = Decimal(
                str(user_latitude)
            ).quantize(
                Decimal("0.000001"),
                rounding=ROUND_HALF_UP
            )

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

        # --------------------------------------------------
        # Get trail step from QR code
        # --------------------------------------------------

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
                    "error": (
                        "Invalid trail-step QR code."
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        trail = trail_step.trail

        # --------------------------------------------------
        # Make sure trail is active
        # --------------------------------------------------

        if not trail.is_active:
            return Response(
                {
                    "error": "Trail is not active."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # --------------------------------------------------
        # Get current active trail attempt
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Existing active attempt
        #
        # IMPORTANT:
        # There is NO step-order restriction.
        # Any incomplete trail step can be scanned.
        # --------------------------------------------------

        if trail_record is not None:

            existing_step_record = (
                TrailStepRecord.objects
                .filter(
                    trail_record=trail_record,
                    step=trail_step
                )
                .first()
            )

            # Prevent completing the same step twice
            # during this trail attempt.
            if (
                existing_step_record is not None
                and existing_step_record.completed
            ):
                return Response(
                    {
                        "message": (
                            "This step has already been "
                            "completed during the current "
                            "attempt."
                        ),
                        "trail_record_id": (
                            trail_record.id
                        ),
                        "step_record_id": (
                            existing_step_record.id
                        ),
                        "attempt_number": (
                            trail_record.attempt_number
                        ),
                    },
                    status=status.HTTP_200_OK
                )

        # --------------------------------------------------
        # No active attempt
        #
        # Any valid trail step may start a new attempt.
        # Step 1 is NOT required anymore.
        # --------------------------------------------------

        if trail_record is None:

            latest_attempt_number = (
                TrailRecord.objects
                .filter(
                    user=user,
                    trail=trail
                )
                .aggregate(
                    maximum=Max(
                        "attempt_number"
                    )
                )["maximum"]
                or 0
            )

            trail_record = (
                TrailRecord.objects.create(
                    user=user,
                    trail=trail,
                    attempt_number=(
                        latest_attempt_number + 1
                    ),
                    status=(
                        TrailRecord.Status.IN_PROGRESS
                    )
                )
            )

            new_attempt_created = True

        # --------------------------------------------------
        # Calculate user's distance from trail step
        # --------------------------------------------------

        distance = self.calculate_distance(
            user_latitude,
            user_longitude,
            float(trail_step.latitude),
            float(trail_step.longitude)
        )

        # calculate_distance returns kilometres.
        #
        # 0.05 km = 50 metres.
        outside_allowed_distance = (
            distance > 0.05
        )

        # --------------------------------------------------
        # Check whether trail continued another day
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Create/update TrailStepRecord
        # --------------------------------------------------

        if existing_step_record is None:

            step_record = (
                TrailStepRecord.objects.create(
                    trail_record=trail_record,
                    step=trail_step,
                    completed=True,
                    scanned_longitude=(
                        user_longitude
                    ),
                    scanned_latitude=(
                        user_latitude
                    ),
                    flagged=should_flag,
                    qr_verified=True,
                )
            )

            # ----------------------------------------------
            # Award points attached directly to this step
            # ----------------------------------------------

            if trail_step.step_reward_points > 0:

                user_profile = (
                    user.customer_profile
                )

                user_profile.total_redeemed_points += (
                    trail_step.step_reward_points
                )

                user_profile.save()

                points_earned = (
                    Earned_Points.objects.create(
                        customer=user,
                        points_earned=(
                            trail_step.step_reward_points
                        )
                    )
                )

                trail_step.points_awarded = True
                trail_step.save()

        else:

            step_record = existing_step_record

            step_record.completed = True
            step_record.qr_verified = True
            step_record.flagged = should_flag

            step_record.save()

        # --------------------------------------------------
        # Calculate trail progress
        # --------------------------------------------------

        total_steps = (
            trail.steps.count()
        )

        completed_steps = (
            trail_record.step_records
            .filter(
                completed=True
            )
            .count()
        )

        flagged_steps = (
            trail_record.step_records
            .filter(
                flagged=True
            )
            .count()
        )

        trail_completed = (
            total_steps > 0
            and completed_steps >= total_steps
        )

        response_message = (
            "Trail step saved successfully."
        )

        pending_verification = False

        # --------------------------------------------------
        # Complete trail
        # --------------------------------------------------

        if trail_completed:

            trail_record.status = (
                TrailRecord.Status.COMPLETED
            )

            trail_record.completed_at = (
                timezone.now()
            )

            trail_record.flagged = (
                flagged_steps > 0
            )

            # ----------------------------------------------
            # Trail contains flagged steps.
            #
            # Complete it but hold final reward/points.
            # ----------------------------------------------

            if flagged_steps > 0:

                pending_verification = True

                trail_record.reward_awarded = False
                trail_record.points_awarded = 0

                response_message = (
                    "Your trail is completed! "
                    "We will verify the steps soon "
                    "so you can get your reward."
                )

            # ----------------------------------------------
            # Physical/attached reward
            # ----------------------------------------------

            elif trail.reward_id is not None:

                reward_assigned = (
                    AssignRewardtoUser(
                        trail,
                        user
                    )
                )

                trail_record.reward_awarded = (
                    reward_assigned
                )

                trail_record.points_awarded = 0

                if reward_assigned:

                    response_message = (
                        "Your trail is completed! "
                        "You have received your reward."
                    )

                else:

                    response_message = (
                        "Your trail is completed, "
                        "but the reward could not "
                        "be assigned."
                    )

            # ----------------------------------------------
            # Trail completion points
            # ----------------------------------------------

            elif trail.reward_points > 0:

                points_assigned = (
                    AssignPointstoUser(
                        trail,
                        user
                    )
                )

                trail_record.reward_awarded = False

                trail_record.points_awarded = (
                    trail.reward_points
                    if points_assigned
                    else 0
                )

                if points_assigned:

                    response_message = (
                        f"Your trail is completed! "
                        f"You have earned "
                        f"{trail.reward_points} points."
                    )

                else:

                    response_message = (
                        "Your trail is completed, "
                        "but the points could not "
                        "be assigned."
                    )

            # ----------------------------------------------
            # No final reward or final points
            # ----------------------------------------------

            else:

                trail_record.reward_awarded = False
                trail_record.points_awarded = 0

                response_message = (
                    "Your trail is completed "
                    "successfully."
                )

            trail_record.save(
                update_fields=[
                    "status",
                    "completed_at",
                    "flagged",
                    "reward_awarded",
                    "points_awarded",
                ]
            )

        # --------------------------------------------------
        # Progress percentage
        # --------------------------------------------------

        progress_percentage = (
            round(
                completed_steps
                / total_steps
                * 100,
                2
            )
            if total_steps > 0
            else 0
        )

        # --------------------------------------------------
        # Suggested next step
        #
        # This is ONLY a suggestion now.
        # User is not required to scan this step next.
        # --------------------------------------------------

        next_step = (
            trail_record.suggested_next_step
        )

        # --------------------------------------------------
        # Badge records
        # --------------------------------------------------

        badge_record = []

        current_badge_level = (
            trail_record.badge_level
        )

        badge_levels = list(
            trail_record.trail.badge.levels.all()
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

            # TrailRecord divides progress
            # into exactly five badge levels.
            required_steps = (
                ceil(
                    index
                    * total_steps
                    / 5
                )
                if total_steps > 0
                else 0
            )

            remaining_steps = max(
                required_steps
                - completed_steps,
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
                "required_steps": (
                    required_steps
                ),
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
                    f"Complete {remaining_steps} "
                    f"more step(s) to pass the "
                    f"{category_name} level."
                )

            badge_record.append(
                badge_item
            )

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

        return Response(
            {
                "message": (
                    response_message
                    if trail_completed
                    else (
                        "Trail step saved "
                        "successfully."
                    )
                ),

                "new_attempt_created": (
                    new_attempt_created
                ),

                "trail_record": {
                    "id": trail_record.id,
                    "trail_id": trail.id,
                    "trail_title": trail.title,

                    "attempt_number": (
                        trail_record.attempt_number
                    ),

                    "status": (
                        trail_record.status
                    ),

                    "reward_awarded": (
                        trail_record.reward_awarded
                        if trail_completed
                        else None
                    ),

                    "points_awarded": (
                        trail_record.points_awarded
                        if trail_completed
                        else None
                    ),
                },

                "scanned_step": {
                    "id": trail_step.id,
                    "title": trail_step.title,
                    "order": trail_step.order,

                    "completed": (
                        step_record.completed
                    ),

                    "flagged": (
                        step_record.flagged
                    ),

                    "qr_verified": (
                        step_record.qr_verified
                    ),

                    "is_step_points_awarded": (
                        True
                        if trail_record.points_awarded > 0
                        else False
                    ),

                    "step_points_awarded": (
                        trail_record.points_awarded
                        if trail_record.points_awarded > 0
                        else None
                    ),

                    "distance_km": round(
                        distance,
                        4
                    ),
                },

                "progress": {
                    "total_steps": (
                        total_steps
                    ),

                    "completed_steps": (
                        completed_steps
                    ),

                    "flagged_steps": (
                        flagged_steps
                    ),

                    "percentage": (
                        progress_percentage
                    ),
                },

                "suggested_next_step": (
                    {
                        "id": next_step.id,
                        "title": next_step.title,
                        "order": next_step.order,

                        "latitude": (
                            next_step.latitude
                        ),

                        "longitude": (
                            next_step.longitude
                        ),
                    }
                    if next_step is not None
                    else None
                ),

                "badge_record": (
                    badge_record
                )
            },

            status=(
                status.HTTP_201_CREATED
                if new_attempt_created
                else status.HTTP_200_OK
            )
        )











# class UserTrailRecordSave(viewsets.GenericViewSet):
#     permission_classes = [IsAuthenticated]

#     def calculate_distance(
#         self,
#         user_latitude,
#         user_longitude,
#         step_latitude,
#         step_longitude
#     ):
#         earth_radius_km = 6371

#         user_latitude = radians(user_latitude)
#         user_longitude = radians(user_longitude)
#         step_latitude = radians(step_latitude)
#         step_longitude = radians(step_longitude)

#         latitude_difference = step_latitude - user_latitude
#         longitude_difference = step_longitude - user_longitude

#         value = (
#             sin(latitude_difference / 2) ** 2
#             + cos(user_latitude)
#             * cos(step_latitude)
#             * sin(longitude_difference / 2) ** 2
#         )

#         return 2 * earth_radius_km * asin(sqrt(value))

#     @transaction.atomic
#     def create(self, request, *args, **kwargs):
#         user = request.user

#         trail_code = str(
#             request.data.get("code", "")
#         ).strip()

#         user_longitude = request.data.get("longitude")
#         user_latitude = request.data.get("latitude")

#         if not trail_code:
#             return Response(
#                 {
#                     "error": "QR code is required."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if user_longitude is None or user_latitude is None:
#             return Response(
#                 {
#                     "error": (
#                         "The user's longitude and latitude "
#                         "are required."
#                     )
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             user_longitude = Decimal(
#                 str(user_longitude)
#             ).quantize(
#                 Decimal("0.000001"),
#                 rounding=ROUND_HALF_UP
#             )

#             user_latitude = Decimal(
#                 str(user_latitude)
#             ).quantize(
#                 Decimal("0.000001"),
#                 rounding=ROUND_HALF_UP
#             )

#         except (TypeError, ValueError):
#             return Response(
#                 {
#                     "error": (
#                         "Longitude and latitude must be "
#                         "valid numbers."
#                     )
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         trail_step = (
#             TrailStep.objects
#             .select_related(
#                 "trail",
#                 "trail__reward",
#                 "qr_code",
#             )
#             .filter(
#                 qr_code__code__iexact=trail_code
#             )
#             .first()
#         )

#         if trail_step is None:
#             return Response(
#                 {
#                     "error": "Invalid trail-step QR code."
#                 },
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         trail = trail_step.trail

#         if not trail.is_active:
#             return Response(
#                 {
#                     "error": "Trail is not active."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Get the user's current active attempt.
#         trail_record = (
#             TrailRecord.objects
#             .select_for_update()
#             .filter(
#                 user=user,
#                 trail=trail,
#                 status=TrailRecord.Status.IN_PROGRESS
#             )
#             .order_by("-attempt_number")
#             .first()
#         )

#         new_attempt_created = False
#         existing_step_record = None

#         if trail_record is not None:
#             existing_step_record = (
#                 TrailStepRecord.objects
#                 .filter(
#                     trail_record=trail_record,
#                     step=trail_step
#                 )
#                 .first()
#             )

#             # Return normally when this step was already completed.
#             if (
#                 existing_step_record is not None
#                 and existing_step_record.completed
#             ):
#                 return Response(
#                     {
#                         "message": (
#                             "This step has already been completed "
#                             "during the current attempt."
#                         ),
#                         "trail_record_id": trail_record.id,
#                         "step_record_id": existing_step_record.id,
#                         "attempt_number": (
#                             trail_record.attempt_number
#                         ),
#                     },
#                     status=status.HTTP_200_OK
#                 )

#             # Get all completed steps for this attempt.
#             completed_step_ids = (
#                 trail_record.step_records
#                 .filter(completed=True)
#                 .values_list("step_id", flat=True)
#             )

#             # The earliest incomplete step is the only allowed step.
#             expected_step = (
#                 trail.steps
#                 .exclude(id__in=completed_step_ids)
#                 .order_by("order")
#                 .first()
#             )

#         else:
#             # There is no active attempt, so only the first trail
#             # step can start a new attempt.
#             expected_step = (
#                 trail.steps
#                 .order_by("order")
#                 .first()
#             )

#         if expected_step is None:
#             return Response(
#                 {
#                     "error": "This trail does not contain any steps."
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Reject a later step when an earlier step is incomplete.
#         if trail_step.id != expected_step.id:
#             return Response(
#                 {
#                     "error": (
#                         "Trail steps must be completed "
#                         "in the correct order."
#                     ),
#                     "expected_step": {
#                         "id": expected_step.id,
#                         "title": expected_step.title,
#                         "order": expected_step.order,
#                     },
#                     "scanned_step": {
#                         "id": trail_step.id,
#                         "title": trail_step.title,
#                         "order": trail_step.order,
#                     },
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Create an attempt only after confirming that the user
#         # scanned the correct step.
#         if trail_record is None:
#             latest_attempt_number = (
#                 TrailRecord.objects
#                 .filter(
#                     user=user,
#                     trail=trail
#                 )
#                 .aggregate(
#                     maximum=Max("attempt_number")
#                 )["maximum"]
#                 or 0
#             )

#             trail_record = TrailRecord.objects.create(
#                 user=user,
#                 trail=trail,
#                 attempt_number=latest_attempt_number + 1,
#                 status=TrailRecord.Status.IN_PROGRESS
#             )

#             new_attempt_created = True

#         distance = self.calculate_distance(
#             user_latitude,
#             user_longitude,
#             float(trail_step.latitude),
#             float(trail_step.longitude)
#         )

#         # calculate_distance() returns kilometres.
#         # 0.05 kilometres equals 50 metres.
#         outside_allowed_distance = distance > 0.05

#         continued_on_another_day = (
#             timezone.localtime(
#                 trail_record.started_at
#             ).date()
#             != timezone.localdate()
#         )

#         should_flag = (
#             outside_allowed_distance
#             or continued_on_another_day
#         )

#         if existing_step_record is None:
#             step_record = TrailStepRecord.objects.create(
#                 trail_record=trail_record,
#                 step=trail_step,
#                 completed=True,
#                 scanned_longitude=user_longitude,
#                 scanned_latitude=user_latitude,
#                 flagged=should_flag,
#                 qr_verified=True,
#             )
#             if trail_step.step_reward_points > 0:
#                 user_profile = user.customer_profile
#                 user_profile.total_redeemed_points += trail_step.step_reward_points
#                 user_profile.save()
#                 points_earned = Earned_Points.objects.create(
#                     customer=user,
#                     points_earned=trail_step.step_reward_points
#                 )
#                 trail_step.points_awarded = True
#                 trail_step.save()
                
#         else:
#             step_record = existing_step_record
#             step_record.completed = True
#             step_record.qr_verified = True
#             step_record.flagged = should_flag
#             step_record.save()

#         total_steps = trail.steps.count()

#         completed_steps = (
#             trail_record.step_records
#             .filter(completed=True)
#             .count()
#         )

#         flagged_steps = (
#             trail_record.step_records
#             .filter(flagged=True)
#             .count()
#         )

#         trail_completed = (
#             total_steps > 0
#             and completed_steps >= total_steps
#         )

#         response_message = "Trail step saved successfully."
#         pending_verification = False

#         if trail_completed:
#             trail_record.status = TrailRecord.Status.COMPLETED
#             trail_record.completed_at = timezone.now()
#             trail_record.flagged = flagged_steps > 0

#             # At least one step is flagged:
#             # complete the trail but hold the reward/points.
#             if flagged_steps > 0:
#                 pending_verification = True
#                 trail_record.reward_awarded = False
#                 trail_record.points_awarded = 0

#                 response_message = (
#                     "Your trail is completed! We will verify the steps "
#                     "soon so you can get your reward."
#                 )

#             # No flagged steps and the trail has a physical reward.
#             elif trail.reward_id is not None:
#                 reward_assigned = AssignRewardtoUser(
#                     trail,
#                     user
#                 )

#                 trail_record.reward_awarded = reward_assigned
#                 trail_record.points_awarded = 0

#                 if reward_assigned:
#                     response_message = (
#                         "Your trail is completed! "
#                         "You have received your reward."
#                     )
#                 else:
#                     response_message = (
#                         "Your trail is completed, but the reward "
#                         "could not be assigned."
#                     )

#             # No attached reward, so award points.
#             elif trail.reward_points > 0:
#                 points_assigned = AssignPointstoUser(
#                     trail,
#                     user
#                 )

#                 trail_record.reward_awarded = False

#                 trail_record.points_awarded = (
#                     trail.reward_points
#                     if points_assigned
#                     else 0
#                 )

#                 if points_assigned:
#                     response_message = (
#                         f"Your trail is completed! You have earned "
#                         f"{trail.reward_points} points."
#                     )
#                 else:
#                     response_message = (
#                         "Your trail is completed, but the points "
#                         "could not be assigned."
#                     )

#             # Trail has neither a reward nor reward points.
#             else:
#                 trail_record.reward_awarded = False
#                 trail_record.points_awarded = 0
#                 response_message = "Your trail is completed successfully."

#             trail_record.save(
#                 update_fields=[
#                     "status",
#                     "completed_at",
#                     "flagged",
#                     "reward_awarded",
#                     "points_awarded",
#                 ]
#             )

#         progress_percentage = (
#             round(
#                 completed_steps / total_steps * 100,
#                 2
#             )
#             if total_steps > 0
#             else 0
#         )

#         next_step = trail_record.suggested_next_step

#         #getting badge records and level of user
#         badge_record = []
#         current_badge_level = (
#             trail_record.badge_level
#         )
#         badge_levels = list(
#             trail_record.trail.badge.levels.all()
#         )
#         for index, badge_level in enumerate(
#             badge_levels,
#             start=1
#         ):
#             category_name = (
#                 badge_level.category.category
#             )

#             level_passed = (
#                 index <= current_badge_level
#             )

#             # The TrailRecord model divides progress
#             # into exactly five badge levels.
#             required_steps = (
#                 ceil(index * total_steps / 5)
#                 if total_steps > 0
#                 else 0
#             )

#             remaining_steps = max(
#                 required_steps - completed_steps,
#                 0
#             )

#             serialized_badge = (
#                 BadgesLevelSerializer(
#                     badge_level,
#                     context={
#                         "request": request
#                     }
#                 ).data
#             )

#             badge_item = {
#                 "level": index,
#                 "badge": serialized_badge,
#                 "status": level_passed,
#                 "required_steps": required_steps,
#             }

#             if level_passed:
#                 badge_item["message"] = (
#                     f"You have passed the "
#                     f"{category_name} level."
#                 )
#             else:
#                 badge_item[
#                     "remaining_steps_to_pass_this_level"
#                 ] = remaining_steps

#                 badge_item["message"] = (
#                     f"Complete {remaining_steps} more "
#                     f"step(s) to pass the "
#                     f"{category_name} level."
#                 )

#             badge_record.append(badge_item)

#         return Response(
#             {
#                 "message": (
#                     response_message
#                     if trail_completed
#                     else "Trail step saved successfully."
#                 ),
#                 "new_attempt_created": new_attempt_created,
#                 "trail_record": {
#                     "id": trail_record.id,
#                     "trail_id": trail.id,
#                     "trail_title": trail.title,
#                     "attempt_number": (
#                         trail_record.attempt_number
#                     ),
#                     "status": trail_record.status,
#                     "reward_awarded": trail_record.reward_awarded if trail_completed else None,
#                     "points_awarded": trail_record.points_awarded if trail_completed else None,
#                 },
#                 "scanned_step": {
#                     "id": trail_step.id,
#                     "title": trail_step.title,
#                     "order": trail_step.order,
#                     "completed": step_record.completed,
#                     "flagged": step_record.flagged,
#                     "qr_verified": step_record.qr_verified,
#                     "is_step_points_awarded": True if trail_record.points_awarded > 0 else False,
#                     "step_points_awarded": trail_record.points_awarded if trail_record.points_awarded > 0 else None,
#                     "distance_km": round(distance, 4),
#                 },
#                 "progress": {
#                     "total_steps": total_steps,
#                     "completed_steps": completed_steps,
#                     "flagged_steps": flagged_steps,
#                     "percentage": progress_percentage,
#                 },
#                 "suggested_next_step": (
#                     {
#                         "id": next_step.id,
#                         "title": next_step.title,
#                         "order": next_step.order,
#                         "latitude": next_step.latitude,
#                         "longitude": next_step.longitude,
#                     }
#                     if next_step is not None
#                     else None
#                 ),
#                 "badge_record": badge_record
#             },
#             status=(
#                 status.HTTP_201_CREATED
#                 if new_attempt_created
#                 else status.HTTP_200_OK
#             )
#         )






