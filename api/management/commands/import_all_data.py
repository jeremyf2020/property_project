import os
import functools
from django.core.management.base import BaseCommand
# --- Imports ---
from api.coordinates.importer import run_coordinate_import
from api.crimes.importer import run_crime_import
from api.schools.importer import (
    run_school_base_import,
    run_ks2_import_wrapper,
    run_ks4_import_wrapper,
    run_ks5_import_wrapper,
)

# --- Decorator 1: Global Lifecycle (Start/End Banners) ---
def log_command_lifecycle(func):
    """
    Prints the 'Starting' and 'Finished' messages
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Starting Global Import ---'))
        try:
            return func(self, *args, **kwargs)
        finally:
            # simple 'finally' ensures this prints even if the script crashes halfway
            self.stdout.write(self.style.SUCCESS('--- All Imports Finished ---'))
    return wrapper

# --- Decorator 2: Task Logger (Per File Logic) ---
def log_task(func):
    """
    Handles the repetitive logic for a single import task:
    1. Print 'Importing X...'
    2. Check file existence (Skip if missing)
    3. Run function
    4. Catch errors
    """
    @functools.wraps(func)
    def wrapper(self, description, file_path, import_func):
        self.stdout.write(f"Importing {description}...")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.WARNING(f"  [SKIP] File not found: {file_path}"))
            return

        try:
            # Run the actual import function passed as argument
            import_func(file_path)
            self.stdout.write(self.style.SUCCESS(f"  [OK] Successfully imported {description}."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  [FAIL] Error in {description}: {e}"))
            
    return wrapper


class Command(BaseCommand):
    help = 'Run all importers sequentially'

    @log_task
    def run_import(self, description, file_path, import_func):
        """
        Helper to trigger the @log_task decorator.
        The body is empty because the decorator does all the work.
        One liner to satisfy the function signature.
        """
        pass 

    @log_command_lifecycle
    def handle(self, *args, **options):
        # Define Folders
        base_dir = 'data'
        school_dir = os.path.join(base_dir, 'school_data')
        # --- Geography ---
        self.run_import(
            "Coordinates", 
            'reading_postcode_sectors.csv', 
            run_coordinate_import)
        # --- Crime ---
        self.run_import(
            "Crime Stats", 
            'detailed_crime_stats.csv', 
            run_crime_import)
        # --- Schools ---
        self.run_import(
            "School Info", 
            os.path.join(school_dir, 'school_information.csv'), 
            lambda path: run_school_base_import(path, year=2024)
        )
        self.run_import(
            "KS2 Results", 
            os.path.join(school_dir, 'key_stage2.csv'), 
            lambda path: run_ks2_import_wrapper(path, year=2024)
        )
        self.run_import(
            "KS4 Results", 
            os.path.join(school_dir, 'key_stage4.csv'), 
            lambda path: run_ks4_import_wrapper(path, year=2024)
        )
        self.run_import(
            "KS5 Results", 
            os.path.join(school_dir, 'key_stage5.csv'), 
            lambda path: run_ks5_import_wrapper(path, year=2024)
        )