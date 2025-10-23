from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from venue.models.menu import Menu_Items
from venue.Serializers.menu_items_serializers import MenuItemsSerializer
from venue.models.menu_categories import Food_Menu_Category


class Venue_Menu_List(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        get_menu_items = Menu_Items.objects.filter(menu_category__venue=pk)
        serialized_data = MenuItemsSerializer(get_menu_items, many=True)
        return Response({"menu": serialized_data.data})