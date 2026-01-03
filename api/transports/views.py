from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from api.transports.models import TransportStop, BusRoute # Note: I used 'transports' (plural) based on your logs
from api.coordinates.models import Coordinates
from .serializers import CommuterSectorSerializer

class CommuterSearchView(APIView):
    """
    Finds neighborhoods with direct bus links to the specific coordinates.
    """
    # This tells Swagger: "I don't use a standard serializer class, but I return a list of CommuterSectorSerializer objects"
    serializer_class = None 

    @extend_schema(
        parameters=[
            OpenApiParameter(name='lat', description='Latitude (e.g. 51.458)', required=True, type=OpenApiTypes.DOUBLE),
            OpenApiParameter(name='lon', description='Longitude (e.g. -0.971)', required=True, type=OpenApiTypes.DOUBLE),
        ],
        responses={200: CommuterSectorSerializer(many=True)}
    )
    def get(self, request):
        try:
            work_lat = float(request.query_params.get('lat'))
            work_lon = float(request.query_params.get('lon'))
        except (TypeError, ValueError):
            # This is why you saw the 400 error!
            return Response({"error": "Please provide 'lat' and 'lon' query parameters"}, status=400)

        # ... (Keep your existing logic here) ...
        # 1. Find Stops
        lat_offset = 0.0045
        lon_offset = 0.007
        
        work_stops = TransportStop.objects.filter(
            latitude__range=(work_lat - lat_offset, work_lat + lat_offset),
            longitude__range=(work_lon - lon_offset, work_lon + lon_offset)
        )

        if not work_stops.exists():
            return Response({"message": "No bus stops found within 500m.", "work_location": {"lat": work_lat, "lon": work_lon}}, status=404)

        # 2. Identify Routes
        work_routes = BusRoute.objects.filter(stops__in=work_stops).distinct()
        work_route_names = list(work_routes.values_list('name', flat=True))

        if not work_route_names:
             return Response({"message": "Stops found, but no active bus routes."}, status=404)

        # 3. Find Neighborhoods
        target_sectors = Coordinates.objects.filter(
            transport_stops__routes__in=work_routes
        ).distinct()

        # 4. Serialize
        serializer = CommuterSectorSerializer(
            target_sectors, 
            many=True, 
            context={'work_routes': work_route_names}
        )

        return Response({
            "search_metadata": {
                "work_location": {"lat": work_lat, "lon": work_lon},
                "nearby_stops_found": work_stops.count(),
                "routes_serving_work": work_route_names
            },
            "results_count": len(serializer.data),
            "recommended_neighborhoods": serializer.data
        })