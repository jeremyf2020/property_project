from api.utils import read_csv_generator
from api.coordinates.models import Coordinates
from .models import CrimeCategory, SectorCrimeStat

def run_crime_import(filename):
    """
    Imports normalized crime data from the aggregated CSV.
    """
    for row in read_csv_generator(filename):
        # Extract sector and remove non-normalized fields
        sector_name = row.pop('postcode_sector', None)
        row.pop('total_crimes', None)
        
        try:
            sector_obj = Coordinates.objects.get(name=sector_name)
            
            for category_name, count_str in row.items():
                if not count_str or not count_str.strip():
                    continue
                
                # Dynamic normalisation: Get or create the category record
                category_obj, _ = CrimeCategory.objects.get_or_create(name=category_name)
                
                # Update or create the link between this sector and this crime type
                SectorCrimeStat.objects.update_or_create(
                    sector=sector_obj,
                    category=category_obj,
                    defaults={'count': int(count_str)}
                )
        except Coordinates.DoesNotExist:
            # Skip if the postcode sector hasn't been imported yet
            continue