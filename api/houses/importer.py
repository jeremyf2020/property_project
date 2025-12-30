from datetime import datetime
from api.houses.models import HouseSaleRecord, HouseFeatures, HouseAddress
from api.utils import read_csv_generator

def get_or_create_address(row):
    """
    Extracts address data from the row and returns a HouseAddress instance.
    """
    address, created = HouseAddress.objects.get_or_create(
        saon=row['saon'],
        paon=row['paon'],
        street=row['street'],
        locality=row['locality'],
        town=row['town'],
        district=row['district'],
        county=row['county'],
        postcode=row['postcode']
    )
    return address

def get_or_create_features(row):
    """
    Extracts feature data from the row and returns a HouseFeatures instance.
    """
    features, created = HouseFeatures.objects.get_or_create(
        type_code=row['property_type'],
        tenure_code=row['estate_type'],
        is_new_build=(row['new_build'] == 'Y'),
        transaction_category=row['transaction_category']
    )
    return features

def create_sale_record(row, address, features, deed_date):
    """
    Creates the HouseSaleRecord linking the address and features.
    """
    sale, created = HouseSaleRecord.objects.get_or_create(
        unique_id=row['unique_id'],
        defaults={
            'price_paid': row['price_paid'],
            'deed_date': deed_date,
            'linked_data_uri': row.get('linked_data_uri', ''),
            'address': address,
            'features': features
        }
    )
    return sale

def import_house_sales(file_path):
    """
    Main function to read CSV and orchestrate the import process.
    """
    sales_created = 0
    csv_generator = read_csv_generator(file_path)
    
    for row in csv_generator:
        # 1. Parse Date
        try:
            deed_date = datetime.strptime(row['deed_date'], '%m/%d/%Y').date()
        except (ValueError, TypeError):
            continue

        # 2. Get Features ID/Object
        features = get_or_create_features(row)

        # 3. Get Address ID/Object
        address = get_or_create_address(row)

        # 4. Create Sale Record using the 2 IDs/Objects
        create_sale_record(row, address, features, deed_date)
        sales_created += 1
        
        # Print progress every 1000 records
        if sales_created % 1000 == 0:
            print(f"Processed {sales_created} records...")

    print(f"Import completed. Total records processed: {sales_created}")