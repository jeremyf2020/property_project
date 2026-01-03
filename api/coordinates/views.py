from rest_framework import viewsets, filters
from .models import Coordinates
from .serializers import CoordinatesSerializer

class CoordinatesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for UK Postcode Sectors (e.g., "RG1 1").
    """
    # 1. Base Query
    queryset = Coordinates.objects.all().order_by('name')
    
    # 2. Serializer
    serializer_class = CoordinatesSerializer

    # 3. Search Capability
    # Allows searching by name: /api/postcode-sectors/?search=RG1
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        """
        Performance Optimization:
        Pre-fetch all related data in a single batch query to prevent 
        N+1 issues when the Serializer accesses properties.
        """
        queryset = super().get_queryset()

        return queryset.prefetch_related(
            # 1. For Crime Stats
            'crime_stats',

            # 2. For Bus Stops AND their Routes (Deep Prefetch)
            'transport_stops', 
            'transport_stops__routes', 

            # 3. For School Names
            'schools' 
        )