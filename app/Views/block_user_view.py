from rest_framework import generics
from app.Permissions.write_by_customer_only_where_obj_user import WriteByCustomerOnlyUser
from app.Serializers.blockSerializer import BlockSerializer
from rest_framework.response import Response
from app.Models.users_blocking import UserBlocking
from rest_framework.permissions import IsAuthenticated


class BlockUserView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated]
    queryset=UserBlocking.objects.all()
    serializer_class=BlockSerializer


    