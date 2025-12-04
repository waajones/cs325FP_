"""
Unit tests for the SimilarityCalculator module.

Tests cosine similarity calculations and recommendation ranking.
Cosine similarity measures how similar two vectors are (1.0 = identical, 0.0 = no similarity).
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from similarity_calculator import SimilarityCalculator
from interfaces import ISimilarityCalculator


class TestSimilarityCalculator(unittest.TestCase):
    """Test cases for SimilarityCalculator."""
    
    def setUp(self):
        """Create a fresh calculator for each test."""
        self.calculator = SimilarityCalculator()
    
    def test_implements_interface(self):
        """Verify SimilarityCalculator implements ISimilarityCalculator (DIP)."""
        self.assertIsInstance(self.calculator, ISimilarityCalculator)
    
    def test_identical_vectors_similarity_is_one(self):
        """Test that identical vectors have similarity of 1.0."""
        vector = [1.0, 2.0, 3.0, 4.0, 5.0]
        similarity = self.calculator.calculate_similarity(vector, vector)
        self.assertAlmostEqual(similarity, 1.0, places=5)
    
    def test_perpendicular_vectors_similarity_is_zero(self):
        """Test that perpendicular vectors have similarity of 0.0."""
        vector1 = [1.0, 0.0, 0.0]
        vector2 = [0.0, 1.0, 0.0]
        similarity = self.calculator.calculate_similarity(vector1, vector2)
        self.assertAlmostEqual(similarity, 0.0, places=5)
    
    def test_empty_vectors_return_zero(self):
        """Test that empty vectors return 0.0 similarity."""
        similarity = self.calculator.calculate_similarity([], [])
        self.assertEqual(similarity, 0.0)
    
    def test_mismatched_dimensions_raises_error(self):
        """Test that mismatched vector dimensions raise ValueError."""
        vector1 = [1.0, 2.0, 3.0]
        vector2 = [1.0, 2.0]
        with self.assertRaises(ValueError):
            self.calculator.calculate_similarity(vector1, vector2)


class TestGetTopRecommendations(unittest.TestCase):
    """Test the get_top_recommendations method."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = SimilarityCalculator()
        self.sample_jobs = [
            {"title": "Job A", "company": "Company A"},
            {"title": "Job B", "company": "Company B"},
            {"title": "Job C", "company": "Company C"},
        ]
    
    def test_returns_correct_number_of_recommendations(self):
        """Test that correct number of recommendations is returned."""
        similarities = [0.9, 0.7, 0.8]
        recommendations = self.calculator.get_top_recommendations(
            self.sample_jobs, similarities, top_n=2
        )
        self.assertEqual(len(recommendations), 2)
    
    def test_recommendations_sorted_by_similarity(self):
        """Test that recommendations are sorted by similarity (highest first)."""
        similarities = [0.5, 0.9, 0.7]
        recommendations = self.calculator.get_top_recommendations(
            self.sample_jobs, similarities, top_n=3
        )
        self.assertEqual(recommendations[0]["title"], "Job B")
    
    def test_recommendations_include_similarity_score(self):
        """Test that recommendations include similarity score."""
        similarities = [0.9, 0.7, 0.8]
        recommendations = self.calculator.get_top_recommendations(
            self.sample_jobs, similarities, top_n=3
        )
        for rec in recommendations:
            self.assertIn("similarity", rec)


if __name__ == '__main__':
    unittest.main()
