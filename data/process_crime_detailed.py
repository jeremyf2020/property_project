import pandas as pd
import os
import glob
from scipy.spatial import cKDTree # Requires: pip install scipy

# Settings
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
SECTOR_FILE = os.path.join(DATA_DIR, 'reading_postcode_sectors.csv')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw_data')
CRIME_DIR = os.path.join(RAW_DATA_DIR, 'crime_data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'detailed_crime_stats.csv')

def main():
    print("--- Starting Corrected Crime Processing (Nearest Neighbor) ---")
    
    # 1. Load Sectors (The "Centers")
    if not os.path.exists(SECTOR_FILE):
        print(f"Error: {SECTOR_FILE} not found.")
        return

    print("Loading sectors...")
    sectors_df = pd.read_csv(SECTOR_FILE)
    
    # Drop rows with missing coordinates (like RG17 3)
    sectors_df = sectors_df.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)
    print(f"Loaded {len(sectors_df)} valid sectors.")

    # 2. Build a KDTree for fast spatial searching
    # This allows us to find the nearest sector for 100k crimes in milliseconds
    print("Building spatial tree...")
    sector_points = sectors_df[['Latitude', 'Longitude']].values
    tree = cKDTree(sector_points)

    # 3. Load ALL Crime Data
    search_pattern = os.path.join(CRIME_DIR, '*', '*street.csv')
    crime_files = glob.glob(search_pattern)
    
    if not crime_files:
        print("No crime files found.")
        return

    print(f"Found {len(crime_files)} monthly files. Merging...")
    
    all_crimes_list = []
    for f in crime_files:
        try:
            # We only need location and type
            df = pd.read_csv(f, usecols=['Latitude', 'Longitude', 'Crime type'])
            df = df.dropna(subset=['Latitude', 'Longitude'])
            all_crimes_list.append(df)
        except Exception as e:
            pass

    if not all_crimes_list:
        print("No valid crime data.")
        return

    crime_df = pd.concat(all_crimes_list, ignore_index=True)
    print(f"Total Crimes Loaded: {len(crime_df)}")

    # 4. Filter to Reading Area (Roughly)
    # This removes crimes from Oxford/Milton Keynes that are in the raw file
    min_lat, max_lat = sectors_df['Latitude'].min() - 0.05, sectors_df['Latitude'].max() + 0.05
    min_lon, max_lon = sectors_df['Longitude'].min() - 0.05, sectors_df['Longitude'].max() + 0.05
    
    crime_df = crime_df[
        (crime_df['Latitude'] >= min_lat) & (crime_df['Latitude'] <= max_lat) &
        (crime_df['Longitude'] >= min_lon) & (crime_df['Longitude'] <= max_lon)
    ]
    print(f"Crimes in Reading Area: {len(crime_df)}")

    # 5. THE FIX: Find Nearest Sector for every single crime
    print("Assigning crimes to nearest sectors...")
    crime_points = crime_df[['Latitude', 'Longitude']].values
    
    # tree.query returns (distances, indices_of_neighbors)
    distances, indices = tree.query(crime_points, k=1)
    
    # Assign the Sector Name based on the index found
    crime_df['closest_sector'] = sectors_df.iloc[indices]['Postcode'].values

    # 6. Aggregate
    print("Aggregating statistics...")
    
    # Group by Sector AND Crime Type -> Count
    stats = crime_df.groupby(['closest_sector', 'Crime type']).size().unstack(fill_value=0)
    
    # Add Total Crimes column
    stats['total_crimes'] = stats.sum(axis=1)
    
    # Reset index to make 'closest_sector' a column
    stats = stats.reset_index().rename(columns={'closest_sector': 'postcode_sector'})

    # 7. Save
    stats.to_csv(OUTPUT_FILE, index=False)
    print(f"Success! Saved cleaner stats to {OUTPUT_FILE}")
    print(stats.head())

if __name__ == "__main__":
    main()