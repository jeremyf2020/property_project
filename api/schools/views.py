from rest_framework import viewsets, filters
from django_filters import rest_framework as django_filters
from .models import School
from .serializers import SchoolSerializer

# --- Custom Filter Class ---
class SchoolFilter(django_filters.FilterSet):
    # map ?phase=Primary to the boolean model fields
    phase = django_filters.CharFilter(method='filter_phase')
    
    # Allow range filtering for age (e.g. ?min_age=4)
    min_age = django_filters.NumberFilter(field_name='minimum_age', lookup_expr='lte')
    max_age = django_filters.NumberFilter(field_name='maximum_age', lookup_expr='gte')

    class Meta:
        model = School
        fields = ['school_type', 'is_closed', 'gender', 'postcode_sector']

    def filter_phase(self, queryset, name, value):
        """
        Custom logic to handle the 'phase' property filter.
        """
        val = value.lower()
        if 'primary' in val:
            return queryset.filter(is_primary=True)
        elif 'secondary' in val:
            return queryset.filter(is_secondary=True)
        elif '16' in val or 'college' in val:
            return queryset.filter(is_post16=True)
        return queryset

# --- ViewSet ---
class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Schools.
    Supports filtering by phase, age, and type.
    """
    serializer_class = SchoolSerializer
    
    # OPTIMIZATION: Prefetch all nested results to prevent N+1 queries
    queryset = School.objects.all().prefetch_related(
        'ks2_results', 
        'ks4_results', 
        'ks5_results'
    ).order_by('name')

    # Enable Filtering & Searching
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SchoolFilter  # Use our custom class defined above
    search_fields = ['name', 'urn', 'postcode']