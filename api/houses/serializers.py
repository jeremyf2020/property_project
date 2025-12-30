from rest_framework import serializers
from api.houses.models import HouseSaleRecord, HouseAddress, HouseFeatures
from api.crimes.serializers import SectorCrimeStatSerializer
from api.schools.serializers import SchoolSerializer

class HouseAddressSerializer(serializers.ModelSerializer):
    postcode_sector = serializers.PrimaryKeyRelatedField(read_only=True)

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
    address = HouseAddressSerializer()
    features = HouseFeaturesSerializer()
    area_crime_stats = serializers.SerializerMethodField()
    nearby_schools = serializers.SerializerMethodField()

    class Meta:
        model = HouseSaleRecord
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Dynamically remove 'area_crime_stats' if we are listing many items
        only want the heavy crime stats when viewing a SINGLE house
        """
        super().__init__(*args, **kwargs)
        
        # Get the current view action (e.g., 'list', 'retrieve', 'create')
        view = self.context.get('view')
        action = getattr(view, 'action', None)
        
        # If the action is 'list', remove the expensive field
        if action == 'list':
            self.fields.pop('area_crime_stats', None)
            self.fields.pop('nearby_schools', None)

    def get_area_crime_stats(self, obj):
        try:
            # Get the sector from the house address
            sector = obj.address.postcode_sector
            
            if sector:
                # Import the model here to be safe from circular import errors
                from api.crimes.models import SectorCrimeStat
                
                # Find all stats for this sector (e.g. Burglary: 5, Anti-social: 10)
                stats = SectorCrimeStat.objects.filter(sector=sector)                
                # Serialize the list of stats
                return SectorCrimeStatSerializer(stats, many=True).data
                
        except AttributeError:
            return []
        return []
    
    def get_nearby_schools(self, obj):
        try:
            sector = obj.address.postcode_sector
            if sector:
                from api.schools.models import School
                schools = School.objects.filter(postcode_sector=sector)
                
                return SchoolSerializer(schools, many=True).data
        except AttributeError:
            return []
        return []

    def update(self, instance, validated_data):
        """
        Updates the HouseSaleRecord. 
        For nested fields (address/features), find/create the new record 
        and re-link the relationship, rather than mutating the old object.
        """
        # Handle Address Update
        if 'address' in validated_data:
            address_data = validated_data.pop('address')
            # Find or create the NEW address definition
            address, _ = HouseAddress.objects.get_or_create(**address_data)
            # Update the link
            instance.address = address

        # Handle Features Update
        if 'features' in validated_data:
            features_data = validated_data.pop('features')
            features, _ = HouseFeatures.objects.get_or_create(**features_data)
            instance.features = features

        # Update standard fields (price, deed_date, etc.)
        return super().update(instance, validated_data)
    
    def create(self, validated_data):
        address_data = validated_data.pop('address')
        features_data = validated_data.pop('features')
        
        address, _ = HouseAddress.objects.get_or_create(**address_data)
        features, _ = HouseFeatures.objects.get_or_create(**features_data)
        
        sale = HouseSaleRecord.objects.create(
            address=address, features=features, **validated_data
        )
        return sale
    
