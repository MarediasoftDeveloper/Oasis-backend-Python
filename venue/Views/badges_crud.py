from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.Permissions.write_by_admin_only import WriteByAdminOnly
from venue.models.badges import Badges
from venue.Serializers.badges_serializer import BadgesSerializer
from rest_framework import viewsets 

class Badges_Crud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, WriteByAdminOnly]
    queryset = Badges.objects.all()
    serializer_class=BadgesSerializer