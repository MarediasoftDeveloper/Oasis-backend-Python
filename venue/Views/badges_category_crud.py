from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.Permissions.write_by_admin_only import WriteByAdminOnly
from venue.models.badge_category import Badge_Category
from venue.Serializers.badge_category_serializer import BadgesCategorySerializer
from rest_framework import viewsets 

class Badges_Category_Crud(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, WriteByAdminOnly]
    queryset = Badge_Category.objects.all()
    serializer_class=BadgesCategorySerializer