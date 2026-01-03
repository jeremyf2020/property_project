from rest_framework import serializers
from api.transports.models import TransportStop, BusRoute
from api.coordinates.models import Coordinates

class TransportStopSerializer(serializers.ModelSerializer):
    """
    Standard serializer for a Bus Stop.
    Output: { "name": "Station Rd", "routes": ["17", "21"] }
    """
    routes = serializers.SlugRelatedField(
        many=True, 
        read_only=True, 
        slug_field='name'
    )

    class Meta:
        model = TransportStop
        fields = ['stop_id', 'name', 'latitude', 'longitude', 'routes']

class CommuterSectorSerializer(serializers.ModelSerializer):
    """
    Specialized serializer for Search Results.
    Output: Neighborhood info + Average Price + WHICH bus gets you to work.
    """
    # These fields are calculated on the fly
    average_price = serializers.SerializerMethodField()
    connected_routes = serializers.SerializerMethodField()
    commute_summary = serializers.SerializerMethodField()

    class Meta:
        model = Coordinates
        fields = [
            'name', 
            'latitude', 
            'longitude', 
            'average_price', 
            'connected_routes', 
            'commute_summary'
        ]

    def get_average_price(self, obj):
        # Checks if you added the field to the model (cached), or returns 0
        return getattr(obj, 'average_price', 0)

    def get_connected_routes(self, obj):
        """
        Returns the specific bus routes that connect THIS sector to the User's Work.
        Logic: Intersection of {Routes in Sector} AND {Routes at Work}
        """
        # 1. Get routes available at user's work (passed from View)
        work_routes = set(self.context.get('work_routes', []))
        
        # 2. Get routes available in this sector (Optimization: Prefetch in View recommended)
        # We access the reverse relationship: sector -> transport_stops -> routes
        sector_routes = set(
            BusRoute.objects.filter(stops__nearest_sector=obj).values_list('name', flat=True)
        )
        
        # 3. Find intersection (The buses you can actually take)
        valid_links = list(work_routes.intersection(sector_routes))
        return sorted(valid_links)

    def get_commute_summary(self, obj):
        routes = self.get_connected_routes(obj)
        if routes:
            return f"Take Bus {', '.join(routes[:2])} directly to there."
        return "No direct route found."