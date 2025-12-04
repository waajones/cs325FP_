"""
Unit tests for the JobRecommendationService.

Demonstrates how dependency injection enables testing by using mock implementations
instead of real services that would make API calls.
"""

import unittest
from unittest.mock import patch
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_recommender import JobRecommendationService
from interfaces import (
    IEmbeddingService,
    IJobScraper,
    IResumeParser,
    ITextProcessor,
    ISimilarityCalculator
)


class MockEmbeddingService(IEmbeddingService):
    """Mock embedding service - returns fake embeddings instead of calling OpenAI."""
    
    def get_embedding(self, text):
        return [0.1] * 1536
    
    def get_embeddings_batch(self, texts, batch_size=20):
        return [[0.1] * 1536 for _ in texts]
    
    def get_embedding_info(self):
        return {"model": "mock", "dimensions": 1536}


class MockJobScraper(IJobScraper):
    """Mock job scraper - returns fake jobs instead of calling Adzuna API."""
    
    def scrape_jobs(self, location, keywords, max_jobs=50, progress_callback=None):
        return [
            {"title": "Software Engineer", "company": "Test Corp",
             "location": location, "description": f"Looking for {keywords}"},
            {"title": "Senior Developer", "company": "Tech Inc",
             "location": location, "description": f"Senior {keywords} needed"},
        ]


class MockResumeParser(IResumeParser):
    """Mock resume parser - returns fake text instead of reading files."""
    
    def parse_file(self, file_path):
        return "Mock resume content with skills and experience"


class MockTextProcessor(ITextProcessor):
    """Mock text processor - simple lowercase and strip."""
    
    def clean_text(self, text, remove_stop_words=False):
        return text.lower().strip()


class MockSimilarityCalculator(ISimilarityCalculator):
    """Mock similarity calculator - returns predictable scores."""
    
    def calculate_similarity(self, vector1, vector2):
        return 0.85
    
    def calculate_similarities(self, resume_embedding, job_embeddings):
        return [0.9, 0.8]
    
    def get_top_recommendations(self, jobs, similarities, top_n=10):
        result = []
        for job, sim in zip(jobs[:top_n], similarities[:top_n]):
            rec = job.copy()
            rec['similarity'] = sim
            result.append(rec)
        return sorted(result, key=lambda x: x['similarity'], reverse=True)


class TestJobRecommendationService(unittest.TestCase):
    """Test JobRecommendationService with mock dependencies."""
    
    def setUp(self):
        """Inject mock dependencies into the service (DIP in action)."""
        self.service = JobRecommendationService(
            job_scraper=MockJobScraper(),
            resume_parser=MockResumeParser(),
            text_processor=MockTextProcessor(),
            embedding_service=MockEmbeddingService(),
            similarity_calculator=MockSimilarityCalculator()
        )
    
    def test_service_initialization(self):
        """Test that service initializes with injected dependencies."""
        self.assertIsNotNone(self.service.job_scraper)
        self.assertIsNotNone(self.service.embedding_service)
    
    @patch('job_recommender.save_stage_output')
    @patch('pandas.DataFrame.to_csv')
    def test_get_recommendations_returns_list(self, mock_csv, mock_save):
        """Test that get_recommendations returns a list of jobs."""
        mock_save.return_value = "mock_path"
        result = self.service.get_recommendations(
            resume_path="fake.pdf", location="NYC", keywords="python"
        )
        self.assertIsInstance(result, list)
    
    @patch('job_recommender.save_stage_output')
    @patch('pandas.DataFrame.to_csv')
    def test_recommendations_have_similarity_score(self, mock_csv, mock_save):
        """Test that each recommendation includes a similarity score."""
        mock_save.return_value = "mock_path"
        result = self.service.get_recommendations(
            resume_path="fake.pdf", location="NYC", keywords="python"
        )
        for rec in result:
            self.assertIn("similarity", rec)


class TestDependencyInjection(unittest.TestCase):
    """Test that injected dependencies are actually used (proves DIP works)."""
    
    def test_custom_job_scraper_is_used(self):
        """Test that injected job scraper is actually used."""
        custom_jobs = [{"title": "Custom Job", "company": "Custom Co",
                       "location": "Custom City", "description": "Custom desc"}]
        
        class CustomJobScraper(IJobScraper):
            def scrape_jobs(self, location, keywords, max_jobs=50, progress_callback=None):
                return custom_jobs
        
        service = JobRecommendationService(
            job_scraper=CustomJobScraper(),
            resume_parser=MockResumeParser(),
            text_processor=MockTextProcessor(),
            embedding_service=MockEmbeddingService(),
            similarity_calculator=MockSimilarityCalculator()
        )
        
        with patch('job_recommender.save_stage_output', return_value="mock"):
            with patch('pandas.DataFrame.to_csv'):
                result = service.get_recommendations("fake.pdf", "Any", "any")
        
        self.assertEqual(result[0]["title"], "Custom Job")


class TestServiceErrorHandling(unittest.TestCase):
    """Test error handling in the service."""
    
    def test_raises_on_empty_resume(self):
        """Test that service raises error when resume parsing fails."""
        class FailingParser(IResumeParser):
            def parse_file(self, file_path):
                return None
        
        service = JobRecommendationService(
            job_scraper=MockJobScraper(),
            resume_parser=FailingParser(),
            text_processor=MockTextProcessor(),
            embedding_service=MockEmbeddingService(),
            similarity_calculator=MockSimilarityCalculator()
        )
        
        with self.assertRaises(ValueError):
            service.get_recommendations("fake.pdf", "NYC", "dev")


if __name__ == '__main__':
    unittest.main()
