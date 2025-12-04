"""
Unit tests for the TextProcessor module.

Tests text cleaning and preprocessing functionality.
Raw text from resumes and job postings contains noise (HTML, URLs, emails)
that must be cleaned before embedding generation.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from text_processor import TextProcessor
from interfaces import ITextProcessor


class TestTextProcessor(unittest.TestCase):
    """Test cases for TextProcessor."""
    
    def setUp(self):
        """Create a fresh processor for each test."""
        self.processor = TextProcessor()
    
    def test_implements_interface(self):
        """Verify TextProcessor implements ITextProcessor (DIP)."""
        self.assertIsInstance(self.processor, ITextProcessor)
    
    def test_clean_text_removes_html_tags(self):
        """Test that HTML tags are removed."""
        text = "<p>Hello <strong>World</strong></p>"
        cleaned = self.processor.clean_text(text)
        self.assertNotIn("<p>", cleaned)
        self.assertIn("hello", cleaned)
    
    def test_clean_text_removes_urls(self):
        """Test that URLs are removed."""
        text = "Visit https://example.com for more info"
        cleaned = self.processor.clean_text(text)
        self.assertNotIn("https://", cleaned)
    
    def test_clean_text_converts_to_lowercase(self):
        """Test that text is converted to lowercase."""
        text = "HELLO World Test"
        cleaned = self.processor.clean_text(text)
        self.assertEqual(cleaned, "hello world test")
    
    def test_clean_text_empty_input(self):
        """Test that empty input returns empty string."""
        self.assertEqual(self.processor.clean_text(""), "")
        self.assertEqual(self.processor.clean_text(None), "")


class TestPrepareJobText(unittest.TestCase):
    """Test the prepare_job_text method."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = TextProcessor()
    
    def test_combines_job_fields(self):
        """Test that job fields are combined into single text."""
        job_data = {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description": "Build amazing products"
        }
        prepared = self.processor.prepare_job_text(job_data)
        self.assertIn("software engineer", prepared)
        self.assertIn("tech corp", prepared)
    
    def test_handles_empty_job_data(self):
        """Test handling of empty job data."""
        prepared = self.processor.prepare_job_text({})
        self.assertEqual(prepared, "")


if __name__ == '__main__':
    unittest.main()
