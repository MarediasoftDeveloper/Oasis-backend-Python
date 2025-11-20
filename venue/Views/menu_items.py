from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.Permissions.write_by_venue_only import WriteByVenueOnlyMenuItem
from venue.models.menu import Menu_Items
from venue.Serializers.menu_items_serializers import MenuItemsSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from app.models import Customer

class Menu_Items_View(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, WriteByVenueOnlyMenuItem]
    serializer_class = MenuItemsSerializer
    
    def get_queryset(self):
        return Menu_Items.objects.filter(menu_category__venue=self.request.user)

     