from unittest.mock import patch
from django.core.management import call_command
from api.management.commands.import_all_data import Command
from django.test import TestCase
from io import StringIO


class ImportAllDataTest(TestCase):
    def test_io_messages(self):
        """
        Test the function havs all correct message
        also mean can run through without interruption.
        """
        out = StringIO()
        call_command('import_all_data', stdout=out)
        self.assertIn('--- Starting Global Import ---', out.getvalue())
        # if there are any error, it should stop, cannot see finish message
        self.assertIn('--- All Imports Finished ---', out.getvalue())

    def test_import_tasks_structure_is_valid(self):
        """
        Check that every task in the registry has the required keys & correct types
        Also, check the function is valid.
        """
        cmd = Command()
        tasks = cmd.import_tasks

        for task in tasks:
            # Check keys exists
            self.assertIn('file', task)
            self.assertIn('function', task)

            # Check types
            self.assertIsInstance(task['file'], str)
            
            # Check function works
            self.assertTrue(
                callable(task['function']), 
                f"Import file: {task['file']} but function is invalid!"
            )