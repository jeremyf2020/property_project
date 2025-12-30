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
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # --- Helper function to clean lists ---
        def clean_results(results_list, required_fields):
            """
            Keeps a record only if at least ONE of the required_fields has a value.
            """
            cleaned = []
            for item in results_list:
                # Check if any of the important fields (reading_score, progress_8, etc.) 
                # is NOT None.
                has_data = any(item.get(field) is not None for field in required_fields)
                if has_data:
                    cleaned.append(item)
            return cleaned

        # Clean KS2 Results
        # Keep record only if it has reading OR maths OR pct score
        cleaned_ks2 = clean_results(data.get('ks2_results', []), ['reading_score', 'maths_score', 'pct_meeting_expected'])
        if cleaned_ks2:
            data['ks2_results'] = cleaned_ks2
        else:
            data.pop('ks2_results', None)

        # Clean KS4 Results
        # Keep record only if it has progress OR attainment
        cleaned_ks4 = clean_results(data.get('ks4_results', []), ['progress_8', 'attainment_8'])
        if cleaned_ks4:
            data['ks4_results'] = cleaned_ks4
        else:
            data.pop('ks4_results', None)

        # Clean KS5 Results
        # Keep record only if it has grade OR points
        cleaned_ks5 = clean_results(data.get('ks5_results', []), ['a_level_grade', 'a_level_points'])
        if cleaned_ks5:
            data['ks5_results'] = cleaned_ks5
        else:
            data.pop('ks5_results', None)

        return data