from django.db import transaction
from rest_framework import serializers

from app.Models.trails.trailModel import Trail
from app.Models.trails.trailSteps import TrailStep
from venue.models.qr_info_model import QR_Info

from app.Serializers.trailSerializers.trail_serializers import TrailSerializer
from venue.Serializers.qr_info_serializer import QRInfoSerializer


class TrailStepSerializer(serializers.ModelSerializer):
    trail = TrailSerializer(read_only=True)
    qr_code = QRInfoSerializer(read_only=True)

    trail_id = serializers.PrimaryKeyRelatedField(
        source="trail",
        queryset=Trail.objects.all(),
        write_only=True
    )

    class Meta:
        model = TrailStep
        fields = [
            "id",
            "trail",
            "trail_id",
            "title",
            "description",
            "featured_image",
            "pin_image",
            "longitude",
            "latitude",
            "qr_code",
            "order",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "trail",
            "qr_code",
            "created_at",
            "updated_at",
        ]

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError(
                "Latitude must be between -90 and 90."
            )

        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError(
                "Longitude must be between -180 and 180."
            )

        return value

    def validate(self, attrs):
        trail = attrs.get(
            "trail",
            getattr(self.instance, "trail", None)
        )

        order = attrs.get(
            "order",
            getattr(self.instance, "order", None)
        )

        if trail is not None and order is not None:
            existing_step = TrailStep.objects.filter(
                trail=trail,
                order=order
            )

            if self.instance is not None:
                existing_step = existing_step.exclude(
                    pk=self.instance.pk
                )

            if existing_step.exists():
                raise serializers.ValidationError({
                    "order": (
                        f"Step order {order} is already used "
                        "for this trail."
                    )
                })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        qr_info = QR_Info()
        qr_info.save()


        trail_step = TrailStep.objects.create(
            qr_code=qr_info,
            **validated_data
        )

        return trail_step