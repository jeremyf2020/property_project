import csv
import os
from collections import defaultdict

# ===========================
# 1. Utility Functions
# ===========================

def read_csv_generator(filename, folder=None):
    """
    Generator that yields clean rows from a CSV file.
    """
    full_path = os.path.join(folder, filename) if folder else filename

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Could not find file: {full_path}")

    with open(full_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {
                (k or '').strip(): (v or '').strip() 
                for k, v in row.items() 
                if k
            }
            yield clean_row

# ===========================
# 2. GTFS Logic Functions
# ===========================

def load_mappings(folder):
    """
    Loads Route and Trip data into memory.
    """
    # 1. Map Route ID -> Short Name (e.g. "RBUS:17" -> "17")
    route_map = {}
    print("   -> Loading Routes...")
    for row in read_csv_generator('routes.txt', folder):
        if row.get('route_id'):
            route_map[row['route_id']] = row.get('route_short_name', 'Unknown')

    # 2. Map Trip ID -> Route ID
    trip_map = {}
    print("   -> Loading Trips...")
    for row in read_csv_generator('trips.txt', folder):
        if row.get('trip_id'):
            trip_map[row['trip_id']] = row.get('route_id')

    return route_map, trip_map

def process_links(folder, trip_map, route_map):
    """
    Scans stop_times.txt and links Stop IDs to Route Names.
    """
    stop_routes = defaultdict(set)
    
    print("   -> Scanning stop_times.txt (this takes a moment)...")
    for row in read_csv_generator('stop_times.txt', folder):
        trip_id = row.get('trip_id')
        stop_id = row.get('stop_id')
        
        if trip_id in trip_map:
            route_id = trip_map[trip_id]
            if route_id in route_map:
                route_name = route_map[route_id]
                stop_routes[stop_id].add(route_name)
                
    return stop_routes

# ===========================
# 3. Main Execution
# ===========================

def convert_gtfs_to_csv():
    # SETTINGS: Use the directory where this script is located
    DATA_FOLDER = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_FILE = os.path.join(DATA_FOLDER, 'bus_stops_with_routes.csv')

    print(f"--- Starting Conversion in '{DATA_FOLDER}' ---")

    try:
        # 1. Load Data
        route_map, trip_map = load_mappings(DATA_FOLDER)
        stop_routes = process_links(DATA_FOLDER, trip_map, route_map)

        # 2. Write Output
        print(f"--- Writing results to {OUTPUT_FILE} ---")
        
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f_out:
            fieldnames = ['stop_id', 'stop_name', 'latitude', 'longitude', 'routes']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()
            
            count = 0
            for row in read_csv_generator('stops.txt', DATA_FOLDER):
                s_id = row.get('stop_id')
                
                # Get linked routes, sort them, join with comma
                routes_list = sorted(list(stop_routes.get(s_id, [])))
                routes_str = ", ".join(routes_list)
                
                writer.writerow({
                    'stop_id': s_id,
                    'stop_name': row.get('stop_name'),
                    'latitude': row.get('stop_lat'),
                    'longitude': row.get('stop_lon'),
                    'routes': routes_str
                })
                count += 1

        print(f"Success! Processed {count} stops.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Please check that 'routes.txt', 'trips.txt', etc. are in the same folder.")

if __name__ == "__main__":
    convert_gtfs_to_csv()