from rest_framework import generics
from app.Permissions.write_by_customer_only_where_obj_user import WriteByCustomerOnlyUser
from app.Serializers.blockSerializer import BlockSerializer
from rest_framework.response import Response
from app.Models.users_blocking import UserBlocking
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets


class BlockUserView(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    serializer_class=BlockSerializer

    def get_queryset(self):
        return UserBlocking.objects.filter(blockedBy=self.request.user)
 
    