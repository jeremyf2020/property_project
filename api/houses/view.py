from rest_framework import viewsets
from api.houses.models import HouseSaleRecord
from api.houses.serializers import HouseSaleSerializer

class HouseSaleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing house sales.
    """
    queryset = HouseSaleRecord.objects.all().order_by('-deed_date')
    serializer_class = HouseSaleSerializer