from rest_framework import serializers
from api.houses.models import HouseSaleRecord, HouseAddress, HouseFeatures

class HouseAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseAddress
        fields = '__all__'


class HouseFeaturesSerializer(serializers.ModelSerializer):
    # These read-only fields provide the human-readable labels (e.g. "Detached")
    property_type_display = serializers.CharField(source='get_type_code_display', read_only=True)
    tenure_type_display = serializers.CharField(source='get_tenure_code_display', read_only=True)

    class Meta:
        model = HouseFeatures
        fields = '__all__'

class HouseSaleSerializer(serializers.ModelSerializer):
    # Use the nested serializers for the ForeignKey fields
    address = HouseAddressSerializer(read_only=True)
    features = HouseFeaturesSerializer(read_only=True)

    class Meta:
        model = HouseSaleRecord
        fields = '__all__'