from rest_framework import serializers
from django.db.models import Sum
from .models import Coordinates
from api.crimes.serializers import SectorCrimeStatSerializer

class CoordinatesSerializer(serializers.ModelSerializer):
    crime_stats = SectorCrimeStatSerializer(many=True, read_only=True)
    # Define a custom field that calls a 'get_...' method
    total_crimes = serializers.SerializerMethodField()

    class Meta:
        model = Coordinates
        fields = [
            'name', 
            'latitude', 
            'longitude', 
            'population', 
            'total_crimes',
            'crime_stats', 
            'nearby_sectors'
        ]

    def get_total_crimes(self, obj):
        """
        Calculates the sum of all crime counts for this specific coordinate.
        Returns 0 if no stats exist.
        """
        # obj is the current Coordinates instance
        result = obj.crime_stats.aggregate(total=Sum('count'))
        return result['total'] or 0