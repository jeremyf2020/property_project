from django.core.management.base import BaseCommand
from api.coordinates.importer import run_coordinate_import
# from api.sales.importer import run_sales_import

class Command(BaseCommand):
    """ 
    Master command to import all data
    """
    import_tasks = [
        {
            'file': 'reading_postcode_sectors.csv',
            'function': run_coordinate_import
        },
        # {
        #     'file': 'reading_house_price.csv',
        #     'function': run_sales_import
        # },
    ]


    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- Starting Global Import ---'))

        # LOOP all the datasets
        for task in self.import_tasks:
            self.stdout.write(f"Importing {task['file']}...")
            try:
                task['function'](task['file'])
                self.stdout.write(self.style.SUCCESS(f"  Successfully imported {task['file']}."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  FAILED to import {task['file']}: {e}"))

        self.stdout.write(self.style.SUCCESS('--- All Imports Finished ---'))