from django.shortcuts import render
from rest_framework import generics 
from app.models import Customer
from venue.Serializers.venue_signup_serializer import Venue_SignUp_Serializer 
from rest_framework.permissions import IsAuthenticated, AllowAny
from venue.Permissions.write_by_venue_only import WriteByVenueOnlyCustom



class Update_Venue(generics.UpdateAPIView):

    permission_classes=[IsAuthenticated, WriteByVenueOnlyCustom]
    queryset = Customer.objects.all()
    serializer_class = Venue_SignUp_Serializer








    