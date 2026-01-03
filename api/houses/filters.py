import django_filters
from django.db.models import Subquery, OuterRef
from .models import HouseSaleRecord
from api.crimes.models import SectorCrimeStat

class HouseSaleFilter(django_filters.FilterSet):
    # Standard filters
    min_price = django_filters.NumberFilter(field_name='price_paid', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_paid', lookup_expr='lte')
    start_date = django_filters.DateFilter(field_name='deed_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='deed_date', lookup_expr='lte')

    # Advanced: Filter by pre-calculated total crimes
    max_sector_crimes = django_filters.NumberFilter(method='filter_by_crime')

    class Meta:
        model = HouseSaleRecord
        fields = ['min_price', 'max_price', 'start_date', 'end_date', 'max_sector_crimes']

    def filter_by_crime(self, queryset, name, value):
        """
        Filters houses where the associated sector's 'total_crimes' stat 
        is less than or equal to the value.
        """
        # 1. Subquery: Find the 'count' from the specific row where category='total_crimes'
        # linked to the house's sector.
        total_crime_subquery = SectorCrimeStat.objects.filter(
            sector=OuterRef('address__postcode_sector'),
            category__name='total_crimes'  # <--- Only look at this specific row
        ).values('count')[:1] # Ensure we return a single value

        # 2. Annotate the House queryset with this single number
        queryset = queryset.annotate(
            sector_total_crimes=Subquery(total_crime_subquery)
        )

        # 3. Filter against the user's input
        return queryset.filter(sector_total_crimes__lte=value)