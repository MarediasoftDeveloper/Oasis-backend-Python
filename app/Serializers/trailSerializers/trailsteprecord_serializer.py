from django.db import transaction
from rest_framework import serializers

from app.Models.trails.trailRecord import TrailRecord
from app.Models.trails.trailSteps import TrailStep
from app.Models.trails.trailStepsRecord import TrailStepRecord









class TrailRecordSummarySerializer(serializers.ModelSerializer):
    trail_title = serializers.CharField(
        source="trail.title",
        read_only=True
    )

    class Meta:
        model = TrailRecord
        fields = [
            "id",
            "trail",
            "trail_title",
            "attempt_number",
            "status",
            "started_at",
            "completed_at",
        ]
        read_only_fields = fields


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


class TrailStepRecordSerializer(serializers.ModelSerializer):
    trail_record = TrailRecordSummarySerializer(read_only=True)
    step = TrailStepSummarySerializer(read_only=True)

    trail_record_id = serializers.PrimaryKeyRelatedField(
        source="trail_record",
        queryset=TrailRecord.objects.select_related(
            "user",
            "trail"
        ).all(),
        write_only=True
    )

    step_id = serializers.PrimaryKeyRelatedField(
        source="step",
        queryset=TrailStep.objects.select_related(
            "trail"
        ).all(),
        write_only=True
    )

    class Meta:
        model = TrailStepRecord
        fields = [
            "id",
            "trail_record",
            "trail_record_id",
            "step",
            "step_id",
            "completed",
            "flagged",
            "qr_verified",
            "completed_at",
            "flagged_at",
        ]

        read_only_fields = [
            "id",
            "trail_record",
            "step",
            "completed_at",
            "flagged_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")

        trail_record = attrs.get(
            "trail_record",
            getattr(self.instance, "trail_record", None)
        )

        step = attrs.get(
            "step",
            getattr(self.instance, "step", None)
        )

        completed = attrs.get(
            "completed",
            getattr(self.instance, "completed", False)
        )

        qr_verified = attrs.get(
            "qr_verified",
            getattr(self.instance, "qr_verified", False)
        )

        if (
            request is None
            or not request.user.is_authenticated
        ):
            raise serializers.ValidationError({
                "error": "Authentication is required."
            })

        if trail_record is None:
            raise serializers.ValidationError({
                "trail_record_id": "A trail record is required."
            })

        if step is None:
            raise serializers.ValidationError({
                "step_id": "A trail step is required."
            })

        # Prevent users from updating another user's trail attempt.
        if trail_record.user_id != request.user.id:
            raise serializers.ValidationError({
                "trail_record_id": (
                    "You cannot modify another user's trail record."
                )
            })

        # The selected step must belong to the same trail.
        if step.trail_id != trail_record.trail_id:
            raise serializers.ValidationError({
                "step_id": (
                    "The selected step does not belong to "
                    "this trail."
                )
            })

        # Steps should only be updated while the attempt is active.
        if trail_record.status != TrailRecord.Status.IN_PROGRESS:
            raise serializers.ValidationError({
                "trail_record_id": (
                    "Steps cannot be updated because this trail "
                    "attempt is no longer in progress."
                )
            })

        # Do not allow changing the trail record or step after creation.
        if self.instance is not None:
            if (
                "trail_record" in attrs
                and trail_record.pk != self.instance.trail_record_id
            ):
                raise serializers.ValidationError({
                    "trail_record_id": (
                        "The trail record cannot be changed."
                    )
                })

            if (
                "step" in attrs
                and step.pk != self.instance.step_id
            ):
                raise serializers.ValidationError({
                    "step_id": (
                        "The trail step cannot be changed."
                    )
                })

        # Optional rule: require QR verification before completion.
        if completed and not qr_verified:
            raise serializers.ValidationError({
                "completed": (
                    "The QR code must be verified before "
                    "the step can be completed."
                )
            })

        duplicate_record = TrailStepRecord.objects.filter(
            trail_record=trail_record,
            step=step
        )

        if self.instance is not None:
            duplicate_record = duplicate_record.exclude(
                pk=self.instance.pk
            )

        if duplicate_record.exists():
            raise serializers.ValidationError({
                "step_id": (
                    "This step already has a record for "
                    "this trail attempt."
                )
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        return TrailStepRecord.objects.create(
            **validated_data
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        # Relationships cannot be changed after creation.
        validated_data.pop("trail_record", None)
        validated_data.pop("step", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        # Calls TrailStepRecord.save(), which automatically sets:
        # completed_at when completed becomes True
        # flagged_at when flagged becomes True
        instance.save()

        return instance