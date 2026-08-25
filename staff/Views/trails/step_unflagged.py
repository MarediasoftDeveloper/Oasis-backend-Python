from rest_framework.views import APIView
from app.Models.trails.trailModel import Trail 
from app.Models.trails.trailStepsRecord import TrailStepRecord
from app.Serializers.trailSerializers.trail_serializers import TrailSerializer 
from app.Serializers.trailSerializers.trailsteprecord_serializer import TrailStepRecordSerializer
from rest_framework.permissions import IsAuthenticated
from staff.Permissions.admin_only_permission import Request_By_Admin_Only
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from app.Views.trials.UsertrialRecordSave import AssignPointstoUser, AssignRewardtoUser

from app.models import Customer
from app.Views.utils.fcm import send_push_notification
import venue








def notify_user_trail_unflagged(user, trail):
        receivers = [user]
        title = (
            f"🎉 Congratulations! Your trail "
            f"'{trail.title}' has been unflagged! ✅"
        )
        body = (
            "🏆 You have successfully completed the trail "
            "and earned your reward! 🎁✨🎉"
        )
        send_push_notification(
            receivers,
            title,
            body,
            data={
                "type": "trail_records_unflagged",  
                "route": "/trailCompletedScreen", 
                "trail_id": str(trail.id), #trailId
            }
        )






class UnflaggedRecordStep(APIView):
    permission_classes = [IsAuthenticated, Request_By_Admin_Only]


    def post(self, request):
        trail_step_record_id = request.data.get("trail_step_record_id")
        unflag_all = request.data.get("unflag_all", False)
        trail_steps_record_by_id = TrailStepRecord.objects.filter(id=trail_step_record_id).first()
        trail_record_all_steps = TrailStepRecord.objects.filter(trail_record_id=trail_steps_record_by_id.trail_record_id)
        trail_steps_record_by_id.flagged = False
        trail_steps_record_by_id.flagged_at = None
        trail_steps_record_by_id.save()

        if not trail_steps_record_by_id:
            return Response({"error": "Trail step record not found."}, status=404)

        if unflag_all:
            trail_record_all_steps.update(flagged=False, flagged_at=None)
        else:
            trail_steps_record_by_id.flagged = False
            trail_steps_record_by_id.flagged_at = None
            trail_steps_record_by_id.save()

        if not trail_record_all_steps.filter(flagged=True).exists():
            if trail_steps_record_by_id.trail_record.trail.reward:
                reward_assigned = (
                    AssignRewardtoUser(trail_steps_record_by_id.trail_record.trail, trail_steps_record_by_id.trail_record.user)
                )
                trail_steps_record_by_id.trail_record.reward_awarded = reward_assigned
            elif trail_steps_record_by_id.trail_record.trail.reward_points:
                points_assigned = (
                    AssignPointstoUser(trail_steps_record_by_id.trail_record.trail, trail_steps_record_by_id.trail_record.user)
                )
                if points_assigned:
                    trail_steps_record_by_id.trail_record.points_awarded = trail_steps_record_by_id.trail_record.trail.reward_points
                else:
                    trail_steps_record_by_id.trail_record.points_awarded = 0
            trail_steps_record_by_id.trail_record.STATUS = "COMPLETED"
            trail_steps_record_by_id.trail_record.flagged = False
            trail_steps_record_by_id.trail_record.save()
            notify_user_trail_unflagged(trail_steps_record_by_id.trail_record.user, trail_steps_record_by_id.trail_record.trail)
            return Response({"message": "All Trail step records unflagged successfully, and the trail record has no flagged steps and reward has been assigned."})
        else:
            return Response({"message": "Trail step record unflagged successfully, but the trail record still has flagged steps."})
            