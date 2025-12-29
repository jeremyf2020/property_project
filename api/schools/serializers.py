from rest_framework import serializers
from .models import School, KS2Performance, KS4Performance, KS5Performance

class KS2Serializer(serializers.ModelSerializer):
    class Meta:
        model = KS2Performance
        fields = ['academic_year', 'reading_score', 'maths_score', 'pct_meeting_expected']

class KS4Serializer(serializers.ModelSerializer):
    class Meta:
        model = KS4Performance
        fields = ['academic_year', 'progress_8', 'attainment_8']

class KS5Serializer(serializers.ModelSerializer):
    class Meta:
        model = KS5Performance
        fields = ['academic_year', 'a_level_grade', 'a_level_points']

class SchoolSerializer(serializers.ModelSerializer):
    # These names must match the 'related_name' in your Models!
    ks2_results = KS2Serializer(many=True, read_only=True)
    ks4_results = KS4Serializer(many=True, read_only=True)
    ks5_results = KS5Serializer(many=True, read_only=True)

    class Meta:
        model = School
        fields = [
            'urn', 'name', 'school_type', 'is_closed', 
            'ks2_results', 'ks4_results', 'ks5_results'
        ]