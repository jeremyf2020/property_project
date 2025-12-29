from unittest.mock import patch
from django.core.management import call_command
from api.management.commands.import_all_data import Command
from django.test import TestCase
from io import StringIO
import os
from unittest.mock import MagicMock, patch
from api.management.commands.import_all_data import log_task

class TaskLoggerDecoratorTest(TestCase):
    def setUp(self):
        # Pre-arrange: mock the mock command object
        self.mock_command = MagicMock()
        self.mock_command.stdout.write = MagicMock()
        self.mock_command.style.SUCCESS = lambda x: f"SUCCESS: {x}"
        self.mock_command.style.WARNING = lambda x: f"WARNING: {x}"
        self.mock_command.style.ERROR = lambda x: f"ERROR: {x}"

        # wrap a dummy function to test the wrapper logic
        @log_task
        def dummy_import_func(self, description, file_path, import_logic):
            import_logic(file_path)
        
        self.decorated_func = dummy_import_func

    def test_logger_file_missing(self):
        """
        Scenario: The CSV file does not exist.
        Expected: Print WARNING, do NOT run the import logic.
        """
        # Arrange: mock logic function
        mock_logic = MagicMock()

        # Act: Execute with missing file
        with patch('os.path.exists', return_value=False):
            self.decorated_func(self.mock_command, "Test Task", "missing.csv", mock_logic)

        # Assertions: should not run and print warning
        mock_logic.assert_not_called() # Should NOT run
        self.mock_command.stdout.write.assert_any_call("WARNING:   [SKIP] File not found: missing.csv")

    def test_logger_success(self):
        """
        Scenario: File exists and import runs fine.
        Expected: Print SUCCESS, Run the import logic.
        """
        # Arrange: mock logic function
        mock_logic = MagicMock()

        # Act: Execute with existing file
        with patch('os.path.exists', return_value=True):
            self.decorated_func(self.mock_command, "Test Task", "exists.csv", mock_logic)

        # Assertions: should run and print success
        mock_logic.assert_called_once_with("exists.csv")
        self.mock_command.stdout.write.assert_any_call("SUCCESS:   [OK] Successfully imported Test Task.")

    def test_logger_exception_handling(self):
        """
        Scenario: File exists but import crashes.
        Expected: Print ERROR, Catch the crash (don't raise).
        """
        # Arrange: mock crash logic function
        mock_logic = MagicMock(side_effect=ValueError("Bad Data"))

        # Act: Execute with existing file
        with patch('os.path.exists', return_value=True):
            self.decorated_func(self.mock_command, "Test Task", "exists.csv", mock_logic)

        # Assertions: should run and print error
        mock_logic.assert_called_once()
        self.mock_command.stdout.write.assert_any_call("ERROR:   [FAIL] Error in Test Task: Bad Data")

class ImportAllDataTest(TestCase):
    def test_io_messages(self):
        """
        Test the function havs start and finish message
        also mean can run through without interruption.
        """
        out = StringIO()
        call_command('import_all_data', stdout=out)
        self.assertIn('--- Starting Global Import ---', out.getvalue())
        # if there are any error, it should stop, cannot see finish message
        self.assertIn('--- All Imports Finished ---', out.getvalue())

    # [TODO: do i need to add more tests here?]

