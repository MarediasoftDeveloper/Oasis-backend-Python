from rest_framework import generics
from app.Permissions.write_by_customer_only_where_obj_user import WriteByCustomerOnlyUser
from app.Serializers.reportAndcomplainSerializer import ReportAndComplainSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.Models.reporting_and_complains import ReportingAndComplains


class ReportingAndComplainsView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated]
    queryset=ReportingAndComplains.objects.all()
    serializer_class=ReportAndComplainSerializer


    