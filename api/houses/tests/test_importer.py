from django.test import TestCase
from unittest.mock import patch, MagicMock, mock_open
from api.houses.importer import import_house_sales

class HouseImporterTestCase(TestCase):
    @patch('builtins.print') 
    @patch('api.houses.importer.create_sale_record')
    @patch('api.houses.importer.get_or_create_address')
    @patch('api.houses.importer.get_or_create_features')
    def test_import_flow(self, mock_features, mock_address, mock_create_sale, mock_print):
        """
        Test that the importer parses the specific real-world data correctly 
        and passes the right values to the creation functions.
        """
        # 1. Prepare Dummy CSV Data using the provided rows
        headers = "unique_id,price_paid,deed_date,postcode,property_type,new_build,estate_type,saon,paon,street,locality,town,district,county,transaction_category,linked_data_uri"
        
        row1 = "34222871-F796-4D2B-E063-4704A8C07853,135740,7/18/2024,RG1 1EQ,F,N,L,FLAT 29,ICON HOUSE,MERCHANTS PLACE,,READING,READING,READING,A,http://landregistry.data.gov.uk/data/ppi/transaction/34222871-F796-4D2B-E063-4704A8C07853/current"
        
        row2 = "402A3A66-AF1F-A7DF-E063-4804A8C0B80D,1265000,10/11/2024,RG1 2AP,O,N,F,FLAT,85,BROAD STREET,,READING,READING,READING,B,http://landregistry.data.gov.uk/data/ppi/transaction/402A3A66-AF1F-A7DF-E063-4804A8C0B80D/current"
        
        csv_content = f"{headers}\n{row1}\n{row2}\n"

        # Mock return values for the helper functions
        mock_features.return_value = MagicMock(id=1)
        mock_address.return_value = MagicMock(id=100)

        # 2. Run Importer with mocked file and functions
        with patch("builtins.open", mock_open(read_data=csv_content)), \
             patch("api.utils.os.path.exists", return_value=True):
            
            import_house_sales("dummy_path.csv")

        # 3. Verify interactions
        
        # Ensure helper functions were called exactly twice (once per row)
        self.assertEqual(mock_features.call_count, 2)
        self.assertEqual(mock_address.call_count, 2)
        self.assertEqual(mock_create_sale.call_count, 2)

        # --- Verify Row 1 Data Passed to create_sale_record ---
        # The first call to create_sale_record corresponds to row 1
        call_args_1 = mock_create_sale.call_args_list[0]
        row_data_1 = call_args_1[0][0] # The 'row' dictionary passed as first arg
        
        self.assertEqual(row_data_1['unique_id'], '34222871-F796-4D2B-E063-4704A8C07853')
        self.assertEqual(row_data_1['price_paid'], '135740')
        self.assertEqual(row_data_1['saon'], 'FLAT 29')
        self.assertEqual(row_data_1['street'], 'MERCHANTS PLACE')
        
        # --- Verify Row 2 Data Passed to create_sale_record ---
        # The second call to create_sale_record corresponds to row 2
        call_args_2 = mock_create_sale.call_args_list[1]
        row_data_2 = call_args_2[0][0]
        
        self.assertEqual(row_data_2['unique_id'], '402A3A66-AF1F-A7DF-E063-4804A8C0B80D')
        self.assertEqual(row_data_2['price_paid'], '1265000')
        self.assertEqual(row_data_2['property_type'], 'O')
        self.assertEqual(row_data_2['transaction_category'], 'B')