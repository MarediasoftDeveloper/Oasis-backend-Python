from rest_framework.permissions import IsAuthenticated, AllowAny
from app.Serializers.friendship_serializer import FriendshipSerializer
from app.Models.friendships import Friendships
from rest_framework import viewsets 
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from app.models import Customer_profile
from app.Permissions.send_by_customer_only import Request_By_Customer_Only
from app.Serializers.customer_profile_serializer import CustomerProfileSerializer


class Friendship_Crud(viewsets.ModelViewSet):
    queryset = Friendships.objects.all()
    permission_classes = [IsAuthenticated, Request_By_Customer_Only]
    serializer_class = FriendshipSerializer
    
    
    def list(self, request, *args, **kwargs):
        friends = Friendships.objects.filter(
            Q(request_sender=request.user, status__in=['pending','declined']) |
            Q(request_getter=request.user, status__in=['pending','declined'])
        )
        data=[]
        for friend in friends:
            if friend.request_sender == request.user:
                get_profile = Customer_profile.objects.get(customer=friend.request_getter)
                serialized_profile = CustomerProfileSerializer(get_profile)
                data.append({
                    'request_send_to':{
                        'friendship_id':friend.id,
                        'request_send_on':friend.send_on,
                        **serialized_profile.data,
                    },
                })
            else:
                get_profile = Customer_profile.objects.get(customer=friend.request_sender)
                serialized_profile = CustomerProfileSerializer(get_profile)
                data.append({
                    'request_get_by':{
                        'friendship_id':friend.id,
                        'request_send_on':friend.send_on,
                        **serialized_profile.data,
                    },
                })
        if not data:
            return Response({"error": "No friends to show!"}, status=404)
        
        return Response(data)
    
    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()

        # Allow only sender or receiver to view the request
        if obj.request_sender != request.user and obj.request_getter != request.user:
            return Response(
                {"error": "You are not allowed to see this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()

        # Allow only sender or receiver to delete
        if obj.request_sender != request.user and obj.request_getter != request.user:
            return Response({"error": "You are not allowed to delete this request."},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(obj)
        return Response({"message": "Friend request deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        