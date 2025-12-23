from rest_framework import viewsets
from .models import Coordinates
from .serializers import CoordinatesSerializer

class CoordinatesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Postcode Sectors to be viewed.
    """
    queryset = Coordinates.objects.all().order_by('name')
    serializer_class = CoordinatesSerializer 