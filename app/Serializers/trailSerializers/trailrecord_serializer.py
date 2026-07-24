from django.db import transaction
from rest_framework import serializers

from app.Models.trails.trailModel import Trail
from app.Models.trails.trailRecord import TrailRecord
from app.Models.trails.trailSteps import TrailStep
from app.Serializers.trailSerializers.trail_serializers import TrailSerializer

from app.Serializers.customer_profile_serializer import CustomerProfileSerializer






class TrailStepSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrailStep
        fields = [
            "id",
            "title",
            "description",
            "featured_image",
            "pin_image",
            "longitude",
            "latitude",
            "order",
        ]
        read_only_fields = fields





class TrailRecordSerializer(serializers.ModelSerializer):
    user = CustomerProfileSerializer(
        source="user.customer_profile",
        read_only=True
    )

    trail = TrailSerializer(read_only=True)

    trail_id = serializers.PrimaryKeyRelatedField(
        source="trail",
        queryset=Trail.objects.filter(is_active=True),
        write_only=True
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True
    )

    started = serializers.BooleanField(read_only=True)
    completed = serializers.BooleanField(read_only=True)
    total_steps = serializers.IntegerField(read_only=True)
    completed_steps_count = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    badge_level = serializers.IntegerField(read_only=True)

    suggested_next_step = TrailStepSummarySerializer(
        read_only=True
    )

    class Meta:
        model = TrailRecord
        fields = [
            "id",
            "user",
            "trail",
            "trail_id",
            "attempt_number",
            "status",
            "status_display",
            "flagged",
            "started",
            "completed",
            "total_steps",
            "completed_steps_count",
            "progress_percentage",
            "badge_level",
            "suggested_next_step",
            "started_at",
            "completed_at",
            "points_awarded",
            "reward_awarded",
        ]

        read_only_fields = [
            "id",
            "user",
            "attempt_number",
            "status",
            "started",
            "completed",
            "total_steps",
            "completed_steps_count",
            "progress_percentage",
            "badge_level",
            "suggested_next_step",
            "started_at",
            "completed_at",
            "points_awarded",
            "reward_awarded",
        ]

    def validate(self, attrs):
        trail = attrs.get(
            "trail",
            getattr(self.instance, "trail", None)
        )

        if trail is None:
            raise serializers.ValidationError({
                "error": "A trail is required."
            })

        if not trail.is_active:
            raise serializers.ValidationError({
                "error": "This trail is not currently active."
            })

        # Do not allow changing the trail after an attempt has started.
        if (
            self.instance is not None
            and "trail" in attrs
            and trail.pk != self.instance.trail_id
        ):
            raise serializers.ValidationError({
                "error": "The trail cannot be changed after an attempt has started."
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")

        if (
            request is None
            or not request.user.is_authenticated
        ):
            raise serializers.ValidationError({
                "error": "An authenticated user is required."
            })

        trail = validated_data["trail"]

        latest_attempt = (
            TrailRecord.objects
            .select_for_update()
            .filter(
                user=request.user,
                trail=trail
            )
            .order_by("-attempt_number")
            .first()
        )

        if latest_attempt is None:
            attempt_number = 1
        else:
            attempt_number = latest_attempt.attempt_number + 1

        return TrailRecord.objects.create(
            user=request.user,
            trail=trail,
            attempt_number=attempt_number,
            status=TrailRecord.Status.IN_PROGRESS,
            **{
                key: value
                for key, value in validated_data.items()
                if key != "trail"
            }
        )