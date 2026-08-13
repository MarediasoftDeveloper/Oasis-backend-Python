from rest_framework import serializers
from app.Models.trails.trailModel import Trail
from app.Serializers.badge_level_serializer import BadgesLevelSerializer
from venue.models.badges import Badges

from rest_framework import serializers

from app.Models.trails.trailModel import Trail
from app.Models.trails.trailRecord import TrailRecord
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer
from venue.models.rewards import Rewards
from venue.Serializers.rewards_serializer import RewardsSerializer
from venue.Serializers.badges_serializer import BadgesSerializer
from venue.models.badges import Badges


class TrailSerializer(serializers.ModelSerializer):
    created_by = CustomerProfileSerializer(
        source="created_by.customer_profile",
        read_only=True)

    reward = RewardsSerializer(read_only=True)
    badge = BadgesSerializer(
         read_only=True
    )

    reward_id = serializers.PrimaryKeyRelatedField(
        source="reward",
        queryset=Rewards.objects.all(),
        write_only=True,
        allow_null=True,
        required=False
    )

    badge_id = serializers.PrimaryKeyRelatedField(
        source="badge",
        queryset=Badges.objects.all(),
        write_only=True,
        allow_null=True,
        required=False
    )

    badge_levels = serializers.SerializerMethodField()

    class Meta:
        model = Trail
        fields = [
            "id",
            "title",
            "description",
            "featured_image",
            "location",
            "instructions",
            "historical_information",
            "reward",
            "reward_id",
            "badge",
            "badge_id",
            "badge_levels",
            "reward_points",
            "created_by",
            "created_at",
            "updated_at",
            "is_active",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "badge_levels"
        ]

    def get_badge_levels(self, obj):
        if obj.badge is None:
            return []

        levels = obj.badge.levels.first()

        return BadgesLevelSerializer(
            levels,
            context=self.context
        ).data

    def validate(self, attrs):
        reward = attrs.get(
            "reward",
            getattr(self.instance, "reward", None)
        )

        reward_points = attrs.get(
            "reward_points",
            getattr(self.instance, "reward_points", 0)
        )

        if reward is not None and reward_points > 0:
            raise serializers.ValidationError({
                "error": "A trail cannot provide both a reward and reward points."
            })

        if reward is None and reward_points == 0:
            raise serializers.ValidationError({
                "error": "Select a reward or provide reward points."
            })

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        if (
            request is None
            or not request.user.is_authenticated
        ):
            raise serializers.ValidationError({
                "error": "An authenticated user is required."
            })

        return Trail.objects.create(
            created_by=request.user,
            **validated_data
        )

    def update(self, instance, validated_data):
        badge = validated_data.pop("badge", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if badge is not None:
            instance.badge = badge
        else:
            instance.badge = None

        instance.save()

        return instance





class TrailGetSerializer(serializers.ModelSerializer):
    steps_count = serializers.IntegerField(
        read_only=True
    )

    badge = BadgesSerializer(
        read_only=True
    )

    started = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    completed_steps_count = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Trail
        fields = [
            "id",
            "title",
            "description",
            "featured_image",
            "location",
            "badge",
            "reward_points",
            "created_at",
            "is_active",
            "steps_count",
            # User-specific trail progress
            "started",
            "completed",
            "completed_steps_count",
            "progress_percentage",
        ]

    def get_user_record(self, obj):
        """
        Returns the requesting user's latest
        TrailRecord for this trail.
        """

        records = getattr(
            obj,
            "request_user_records",
            []
        )

        if not records:
            return None

        return records[0]

    def get_started(self, obj):
        """
        True if the requesting user has
        started this trail.
        """

        return self.get_user_record(obj) is not None

    def get_completed(self, obj):
        """
        True if the user's latest trail
        attempt is completed.
        """

        record = self.get_user_record(obj)

        if record is None:
            return False

        return (
            record.status
            == TrailRecord.Status.COMPLETED
        )

    def get_completed_steps_count(self, obj):
        """
        Number of completed steps in the
        user's latest attempt.
        """

        record = self.get_user_record(obj)

        if record is None:
            return 0

        completed_records = getattr(
            record,
            "completed_step_records",
            []
        )

        return len(completed_records)

    def get_progress_percentage(self, obj):
        """
        Percentage of trail steps completed
        in the user's latest attempt.
        """

        record = self.get_user_record(obj)

        if record is None:
            return 0

        total_steps = getattr(
            obj,
            "steps_count",
            0
        )

        if total_steps == 0:
            return 0

        completed_records = getattr(
            record,
            "completed_step_records",
            []
        )

        completed_steps = len(
            completed_records
        )

        return round(
            (
                completed_steps
                / total_steps
            ) * 100,
            2
        )