from api.utils import read_csv_generator
from api.coordinates.models import Coordinates

def parse_coordinate_row(row):
    """
    Parses a python dictionary from the CSV.
    """
    return {
        'name': row.get('Postcode'),
        'latitude': float(row['Latitude']) if row.get('Latitude') and row['Latitude'].strip() else None,
        'longitude': float(row['Longitude']) if row.get('Longitude') and row['Longitude'].strip() else None,
        'population': int(row['Population']) if row.get('Population') and row['Population'].strip() else 0,
        'raw_neighbors': [n.strip() for n in row.get('Nearby Sectors', '').split(',') if n.strip()]
    }

def loop_csv(filename):
    """
    Loop though the csv file:
    1. save/update the coordinates
    2. return neighbor map for next step: nearby sectors 
    """
    neighbor_map = {}
    
    for row in read_csv_generator(filename):
        data = parse_coordinate_row(row)
        name = data.pop('name') # Extract name to use as lookup
        raw_neighbors = data.pop('raw_neighbors')
        
        # Save basic record
        Coordinates.objects.update_or_create(name=name, defaults=data)
        
        # Store for second pass
        if raw_neighbors:
            neighbor_map[name] = raw_neighbors
            
    return neighbor_map

def link_all_neighbors(neighbor_map):
    """
    Establish Many-to-Many relationships based on the map (return from loop).
    """
    for sector_name, neighbors in neighbor_map.items():
        try:
            main_sector = Coordinates.objects.get(name=sector_name)
            neighbor_objs = Coordinates.objects.filter(name__in=neighbors)
            main_sector.nearby_sectors.set(neighbor_objs)
        except Coordinates.DoesNotExist:
            continue

def run_coordinate_import(filename='reading_postcode_sectors.csv'):
    """
    Master function to coordinate the process.
    """
    neighbor_map = loop_csv(filename)
    link_all_neighbors(neighbor_map)