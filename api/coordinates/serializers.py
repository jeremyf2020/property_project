from rest_framework import serializers
from django.db.models import Sum
from .models import Coordinates
from api.crimes.serializers import SectorCrimeStatSerializer
from drf_spectacular.utils import extend_schema_field
from api.transports.serializers import TransportStopSerializer

class CoordinatesSerializer(serializers.ModelSerializer):
    crime_stats = SectorCrimeStatSerializer(many=True, read_only=True)
    total_crimes = serializers.SerializerMethodField()
    crime_rate = serializers.SerializerMethodField()

    average_price = serializers.IntegerField(source='area_average_price', read_only=True) 
    total_bus_stops = serializers.IntegerField(source='bus_stop_count', read_only=True)   
    nearby_bus_stops = serializers.SerializerMethodField() 
    school_names = serializers.SerializerMethodField()     

    class Meta:
        model = Coordinates
        fields = [
            'name', 
            'latitude', 
            'longitude', 
            'population', 
            'total_crimes',
            'households',
            'crime_rate', 
            'crime_stats', 
            'nearby_sectors',
            'average_price',     
            'total_bus_stops',   
            'nearby_bus_stops',  
            'school_names',      
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lazy Loading: Hide heavy lists if we are just listing all sectors
        if self.context.get('view') and self.context.get('view').action == 'list':
            self.fields.pop('crime_stats', None)
            self.fields.pop('nearby_bus_stops', None)
            self.fields.pop('school_names', None)

    @extend_schema_field(TransportStopSerializer(many=True))
    def get_nearby_bus_stops(self, obj):
        # Uses the helper method from your Model
        return TransportStopSerializer(obj.get_stops_with_routes(), many=True).data

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_school_names(self, obj):
        # Uses the helper method from your Model
        return obj.get_school_names()

    def get_total_crimes(self, obj):
        """
        Finds the total_crimes row and returns its count directly.
        """
        total_stat = obj.crime_stats.filter(category__name='total_crimes').first()
        
        if total_stat:
            return total_stat.count
        return 0

    def get_crime_rate(self, obj):
        """
        Returns crimes per 100 households.
        Formula: (Total Crimes / Total Households) * 100 
        """
        # Get the values safely (default to 0 if missing)
        crimes = self.get_total_crimes(obj)
        houses = getattr(obj, 'households', 0) 

        # Avoid division by zero
        if houses == 0:
            return 0.0

        # Calculate and round
        rate = (crimes / houses) * 100
        return round(rate, 2)


class SectorSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight summary of a neighborhood.
    Used for embedding in other APIs (Houses, Schools, etc).
    """
    crime_rate = serializers.FloatField(source='current_crime_rate', read_only=True)
    bus_stop_count = serializers.IntegerField(source='bus_stop_count', read_only=True)
    average_price = serializers.IntegerField(source='area_average_price', read_only=True)
    school_names = serializers.SerializerMethodField()

    class Meta:
        model = Coordinates
        fields = [
            'name',         
            'crime_rate', 
            'bus_stop_count', 
            'average_price', 
            'school_names'
        ]

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_school_names(self, obj):
        return obj.get_school_names()