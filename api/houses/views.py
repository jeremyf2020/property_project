from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from api.houses.models import HouseSaleRecord
from api.houses.serializers import HouseSaleSerializer

from api.houses.filters import HouseSaleFilter 

class HouseSaleViewSet(viewsets.ModelViewSet):
    queryset = HouseSaleRecord.objects.all().order_by('-deed_date')
    serializer_class = HouseSaleSerializer
    
    filter_backends = [DjangoFilterBackend]
    filterset_class = HouseSaleFilter