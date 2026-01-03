from rest_framework import serializers
from api.houses.models import HouseSaleRecord, HouseAddress, HouseFeatures
from api.crimes.serializers import SectorCrimeStatSerializer
from api.schools.serializers import SchoolSerializer
from drf_spectacular.utils import extend_schema_field

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

    # Heavy Details (Detail View Only)
    area_crime_stats = serializers.SerializerMethodField()
    nearby_schools = serializers.SerializerMethodField()
    nearby_bus_stops = serializers.SerializerMethodField()
    
    # Lightweight Summaries (List View & Detail View)
    total_crimes = serializers.SerializerMethodField()
    crime_rate = serializers.SerializerMethodField()
    total_bus_stops = serializers.SerializerMethodField()

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
        if view and hasattr(view, 'action'):        
            if view.action == 'list':
                # LIST VIEW: Remove heavy lists, keep summaries
                self.fields.pop('area_crime_stats', None)
                # self.fields.pop('nearby_schools', None)
                # We also remove bus stop count from list to keep it fast
                self.fields.pop('nearby_bus_stops', None)

    @extend_schema_field(SchoolSerializer(many=True))
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
    
    @extend_schema_field(dict)
    def get_nearby_schools(self, obj):
        try:
            sector = obj.address.postcode_sector
            if not sector:
                return []

            # Determine if we are in List or Detail view
            view = self.context.get('view')
            is_list_view = view and view.action == 'list'

            # Define the base query (Lazy - doesn't run yet)
            from api.schools.models import School
            schools_qs = School.objects.filter(postcode_sector=sector)

            if is_list_view:
                # OPTIMIZATION: Only fetch the 'name' column. 
                # Returns: ["Reading School", "Kendrick School"]
                return list(schools_qs.values_list('name', flat=True))
            
            else:
                # DETAIL VIEW: Use the full serializer
                # Returns: [{ "name": "Reading School", "urn": "123", ... }]
                return SchoolSerializer(schools_qs, many=True).data

        except AttributeError:
            pass
        return []    
    
    @extend_schema_field(int)
    def get_total_bus_stops(self, obj):
        """Count of bus stops in this sector"""
        try:
            sector = obj.address.postcode_sector
            if sector:
                from api.transports.models import TransportStop
                return TransportStop.objects.filter(nearest_sector=sector).count()
        except (AttributeError, ImportError):
            pass
        return 0

    @extend_schema_field(list)
    def get_nearby_bus_stops(self, obj):
        try:
            sector = obj.address.postcode_sector
            if not sector:
                return []

            from api.transports.models import TransportStop
            # Use prefetch_related to load routes efficiently
            stops = TransportStop.objects.filter(
                nearest_sector=sector
            ).prefetch_related('routes')

            data = []
            for stop in stops:
                data.append({
                    "stop_name": stop.name,
                    "stop_id": stop.stop_id,
                    "routes": [r.name for r in stop.routes.all()]
                })
            return data

        except (AttributeError, ImportError):
            pass
        return []

    @extend_schema_field(int)
    def get_total_crimes(self, obj):
        """
        Finds the specific row where category='total_crimes' and returns its count.
        (precalculated from the csv)
        """
        try:
            sector = obj.address.postcode_sector
            if sector:
                from api.crimes.models import SectorCrimeStat
                
                # FIX: Don't use Sum(). Just find the specific "total_crimes" row.
                stat = SectorCrimeStat.objects.filter(
                    sector=sector, 
                    category__name='total_crimes'
                ).first()
                
                return stat.count if stat else 0
                
        except (AttributeError, ImportError):
            pass
        return 0    
    
    @extend_schema_field(float)
    def get_crime_rate(self, obj):
        """Crimes per 1,000 households"""
        try:
            sector = obj.address.postcode_sector
            if sector:
                # 1. Get Crime Count
                total_crimes = self.get_total_crimes(obj)
                
                # 2. Get House Count (Assuming 'households' exists on Coordinates model)
                # If your Coordinate model doesn't have households, default to 1 to avoid ZeroDivision
                house_count = getattr(sector, 'households', 0)
                
                if house_count > 0:
                    return round((total_crimes / house_count) * 1000, 2)
        except AttributeError:
            pass
        return 0.0

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
    
