from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.Permissions.write_by_venue_only import WriteByVenueOnly
from venue.models.menu_categories import Food_Menu_Category
from venue.Serializers.menu_category import FoodMenuCategorySerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from app.models import Customer

class Menu_Category_View(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, WriteByVenueOnly]
    serializer_class = FoodMenuCategorySerializer

    
    def get_queryset(self):
        return Food_Menu_Category.objects.filter(venue=self.request.user)

     