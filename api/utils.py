import csv
import os
from django.conf import settings

def read_csv_generator(filename, folder="data"):
    """
    Generator that yields rows from a CSV file one by one.
    """
    full_path = os.path.join(settings.BASE_DIR, folder, filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Could not find file at: {full_path}")

    with open(full_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
            yield clean_row

