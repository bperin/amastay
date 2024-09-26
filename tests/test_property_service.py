import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.property_service import PropertyService


class TestPropertyService(unittest.TestCase):

    @patch('property_service.supabase_client')
    def test_get_all_properties(self, mock_supabase_client):
        # Mock the response from Supabase
        mock_supabase_client.from_().select().execute.return_value = MagicMock(data=[{"id": "1", "name": "Test Property"}], error=None)
        
        result = PropertyService.get_all_properties()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]['name'], "Test Property")
    
    @patch('property_service.supabase_client')
    def test_get_property_by_id(self, mock_supabase_client):
        # Mock the response from Supabase
        mock_supabase_client.from_().select().eq().execute.return_value = MagicMock(data=[{"id": "1", "name": "Test Property"}], error=None)
        
        result = PropertyService.get_property_by_id("1")
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], "Test Property")
    
    @patch('property_service.Scraper')
    @patch('property_service.supabase_client')
    def test_create_property_with_scraping(self, mock_supabase_client, MockScraper):
        # Mock the response from Supabase
        mock_supabase_client.from_().insert().select().execute.return_value = MagicMock(data=[{"id": "1"}], error=None)
        
        # Mock the scraper's methods
        mock_scraper_instance = MockScraper.return_value
        mock_scraper_instance.scrape.return_value = "Mock scraped data"
        mock_scraper_instance.save_scraped_data.return_value = "mock_file.txt"

        property_data = {
            "owner_id": "some-owner-uuid",
            "name": "Test Property with Scraping",
            "description": "This is a test property with URL",
            "address": "123 Test St",
            "lat": 10.0,
            "lng": 20.0,
            "url": "http://example.com/test-property"
        }

        result = PropertyService.create_property(property_data)
        self.assertIsNotNone(result)
        self.assertEqual(result['message'], "Property created successfully")

        # Assert that the scraper's methods were called
        mock_scraper_instance.scrape.assert_called_once()
        mock_scraper_instance.save_scraped_data.assert_called_once_with("1", "Mock scraped data")

    @patch('property_service.supabase_client')
    def test_create_property_without_scraping(self, mock_supabase_client):
        # Mock the response from Supabase
        mock_supabase_client.from_().insert().select().execute.return_value = MagicMock(data=[{"id": "1"}], error=None)
        
        property_data = {
            "owner_id": "some-owner-uuid",
            "name": "Test Property without Scraping",
            "description": "This is a test property",
            "address": "123 Test St",
            "lat": 10.0,
            "lng": 20.0
        }

        result = PropertyService.create_property(property_data)
        self.assertIsNotNone(result)
        self.assertEqual(result['message'], "Property created successfully")

    @patch('property_service.supabase_client')
    def test_update_property(self, mock_supabase_client):
        # Mock the response from Supabase
        mock_supabase_client.from_().update().eq().select().execute.return_value = MagicMock(data=[{"id": "1", "description": "Updated Description"}], error=None)

        updates = {"description": "Updated Description"}
        result = PropertyService.update_property("1", updates)
        self.assertIsNotNone(result)
        self.assertEqual(result['description'], "Updated Description")
    
    @patch('property_service.supabase_client')
    def test_delete_property(self, mock_supabase_client):
        # Mock the response from Supabase
        mock_supabase_client.from_().delete().eq().execute.return_value = MagicMock(data=[], error=None)

        result = PropertyService.delete_property("1")
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
