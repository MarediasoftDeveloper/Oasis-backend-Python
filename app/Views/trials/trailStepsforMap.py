
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from app.Models.trails.trailModel import Trail
from app.Models.trails.trailRecord import TrailRecord
from app.Models.trails.trailSteps import TrailStep
from app.Serializers.trailSerializers.trail_serializers import TrailSerializer, TrailGetSerializer
from app.Serializers.trailSerializers.trailstep_serializer import TrailStepSerializerForMap
from django.db.models.expressions import RawSQL
from django.db.models import Q, F, Prefetch, FloatField, Min, Case, When, IntegerField, Count
from django.db.models.functions import ACos, Cos, Sin, Radians
from django.utils import timezone


class TrailStepsMap(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        user = self.request.user
        user_trail_ids = (
            TrailRecord.objects
            .filter(
                user=user,
                trail__is_garden=True
            )
            .values_list(
                "trail_id",
                flat=True
            )
            .distinct()
        )

        steps = TrailStep.objects.filter(
        Q(
            trail__is_active=True,
            trail__is_garden=False
        )
        |
        Q(
            trail__is_active=True,
            trail__is_garden=True,
            trail__id__in=user_trail_ids
        )
        ).order_by("trail_id", "order")
        Serializer = TrailStepSerializerForMap(steps, many=True)
        serialized_data = Serializer.data    
        return Response(serialized_data)

      