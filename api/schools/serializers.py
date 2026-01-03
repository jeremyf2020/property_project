from rest_framework import serializers
from .models import School, KS2Performance, KS4Performance, KS5Performance
from api.coordinates.serializers import SectorSummarySerializer

class KS2Serializer(serializers.ModelSerializer):
    class Meta:
        model = KS2Performance
        fields = ['academic_year', 'pct_meeting_expected', 'reading_score', 'maths_score']

class KS4Serializer(serializers.ModelSerializer):
    class Meta:
        model = KS4Performance
        fields = ['academic_year', 'progress_8', 'attainment_8']

class KS5Serializer(serializers.ModelSerializer):
    class Meta:
        model = KS5Performance
        fields = ['academic_year', 'a_level_points', 'a_level_grade', 'academic_points', 'academic_grade']

class SchoolSerializer(serializers.ModelSerializer):
    # Nested Serializers (Read Only)
    ks2_results = KS2Serializer(many=True, read_only=True)
    ks4_results = KS4Serializer(many=True, read_only=True)
    ks5_results = KS5Serializer(many=True, read_only=True)

    # We explicitly include the property fields
    phase = serializers.ReadOnlyField() 
    age_range = serializers.ReadOnlyField(source='age_range_str')

    # neighborhood_summary = SectorSummarySerializer(
    #     source='postcode_sector', 
    #     read_only=True
    # )

    class Meta:
        model = School
        fields = [
            'urn', 'name', 'street', 'locality', 'postcode', 
            'school_type', 'is_closed', 'gender', 
            'is_primary', 'is_secondary', 'is_post16', 
            'phase', 'age_range', 'postcode_sector',
            'ks2_results', 'ks4_results', 'ks5_results'
        ]

    def to_representation(self, instance):
        """
        Custom logic to remove empty result arrays from the final response.
        """
        # 1. Get the standard dictionary data
        data = super().to_representation(instance)

        # 2. Check and remove empty lists
        # keys matches the field names in 'fields' above
        for key in ['ks2_results', 'ks4_results', 'ks5_results']:
            if not data.get(key):  # If list is empty [] or None
                data.pop(key, None)

        return data