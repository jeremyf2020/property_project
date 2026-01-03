import sys
from api.transports.models import TransportStop, BusRoute
from api.coordinates.models import Coordinates
from api.utils import read_csv_generator, clean_decimal

# ==========================================
# Main Entry Point
# ==========================================

def run_transport_import(file_path):
    """
    Imports transport data from a full file path.
    Wrapper handles 'Starting'/'Finished' messages.
    """
    # 1. Prepare Caches
    sectors_cache = _get_sector_cache()
    existing_routes_cache = _get_existing_routes_cache()
    
    if not sectors_cache:
        print("Warning: No sectors found. Transport stops will not be linked to neighborhoods.")

    count = 0
    
    # 2. Iterate
    # We pass folder="" because file_path is already a full absolute path from import_all_data
    for row in read_csv_generator(file_path, folder=""):
        
        # 3. Process Data
        stop_data = _extract_stop_data(row)
        if not stop_data: 
            continue

        # 4. Geometry Logic
        nearest_sector_id = _find_nearest_sector(
            stop_data['lat'], 
            stop_data['lon'], 
            sectors_cache
        )

        # 5. DB Save (Stop)
        stop_obj = _save_transport_stop(stop_data, nearest_sector_id)

        # 6. DB Save (Routes M2M)
        _link_routes_to_stop(stop_obj, row.get('routes'), existing_routes_cache)
        
        count += 1
        
        # Progress Printer (Every 200 steps)
        if count % 200 == 0:
            print(f"Processed {count} stops...")

    print(f"Import completed. Total stops processed: {count}")

# ==========================================
# Sub-Routines
# ==========================================

def _get_sector_cache():
    return list(Coordinates.objects.values_list('name', 'latitude', 'longitude'))


def _get_existing_routes_cache():
    return set(BusRoute.objects.values_list('name', flat=True))


def _extract_stop_data(row):
    lat = clean_decimal(row.get('latitude'))
    lon = clean_decimal(row.get('longitude'))
    stop_id = row.get('stop_id')
    stop_name = row.get('stop_name')

    if not stop_id or lat is None or lon is None:
        return None

    return {
        'stop_id': stop_id,
        'name': stop_name,
        'lat': lat,
        'lon': lon
    }


def _find_nearest_sector(lat, lon, sectors_cache):
    closest = None
    min_dist = float('inf')
    
    for name, s_lat, s_lon in sectors_cache:
        if s_lat is None or s_lon is None: 
            continue
        
        dist = (s_lat - lat)**2 + (s_lon - lon)**2
        
        if dist < min_dist:
            min_dist = dist
            closest = name
            
    return closest


def _save_transport_stop(data, sector_id):
    stop, _ = TransportStop.objects.update_or_create(
        stop_id=data['stop_id'],
        defaults={
            'name': data['name'],
            'latitude': data['lat'],
            'longitude': data['lon'],
            'nearest_sector_id': sector_id
        }
    )
    return stop


def _link_routes_to_stop(stop_obj, route_string, existing_routes_cache):
    if not route_string:
        return

    route_names = [r.strip() for r in route_string.split(',') if r.strip()]
    if not route_names:
        return

    # Create new routes if needed
    new_routes = [r for r in route_names if r not in existing_routes_cache]
    if new_routes:
        BusRoute.objects.bulk_create([BusRoute(name=r) for r in new_routes], ignore_conflicts=True)
        existing_routes_cache.update(new_routes)
    
    # Link to Stop
    routes_objs = BusRoute.objects.filter(name__in=route_names)
    stop_obj.routes.set(routes_objs)