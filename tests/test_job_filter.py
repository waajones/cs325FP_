"""
Unit tests for the JobFilter module.

Tests job filtering functionality based on salary, experience, job type, and skills.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_filter import JobFilter


class TestJobFilter(unittest.TestCase):
    """Test cases for JobFilter."""
    
    def setUp(self):
        """Create sample jobs for testing."""
        self.sample_jobs = [
            {
                "title": "Senior Software Engineer",
                "description": "5+ years Python experience required",
                "salary": "$150,000",
                "job_type": "Full-time"
            },
            {
                "title": "Junior Developer",
                "description": "Entry level position, JavaScript needed",
                "salary": "$60,000",
                "job_type": "Full-time"
            },
            {
                "title": "Lead Data Scientist",
                "description": "Lead ML team, Python required",
                "salary": None,
                "job_type": "Contract"
            },
        ]
    
    def test_no_filters_returns_all(self):
        """Test that no filters returns all jobs."""
        result = JobFilter.filter_jobs(self.sample_jobs)
        self.assertEqual(len(result), 3)
    
    def test_filter_by_minimum_salary(self):
        """Test filtering by minimum salary."""
        result = JobFilter.filter_jobs(self.sample_jobs, salary_min=100000)
        self.assertEqual(len(result), 2)
    
    def test_filter_by_experience_level(self):
        """Test filtering for senior level jobs."""
        result = JobFilter.filter_jobs(self.sample_jobs, experience_levels=["Senior"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Senior Software Engineer")
    
    def test_filter_by_job_type(self):
        """Test filtering for full-time jobs."""
        result = JobFilter.filter_jobs(self.sample_jobs, job_types=["Full-time"])
        self.assertEqual(len(result), 2)
    
    def test_filter_by_skills(self):
        """Test filtering for Python skill."""
        result = JobFilter.filter_jobs(self.sample_jobs, required_skills=["Python"])
        self.assertEqual(len(result), 2)


class TestCombinedFilters(unittest.TestCase):
    """Test combining multiple filters."""
    
    def setUp(self):
        """Create sample jobs for testing."""
        self.sample_jobs = [
            {
                "title": "Senior Python Developer",
                "description": "Senior level Python role",
                "salary": "$150,000",
                "job_type": "Full-time"
            },
            {
                "title": "Junior Python Developer",
                "description": "Entry level Python role",
                "salary": "$70,000",
                "job_type": "Full-time"
            },
        ]
    
    def test_combined_all_filters(self):
        """Test combining salary, experience, job type, and skills filters."""
        result = JobFilter.filter_jobs(
            self.sample_jobs,
            salary_min=100000,
            experience_levels=["Senior"],
            job_types=["Full-time"],
            required_skills=["Python"]
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Senior Python Developer")


if __name__ == '__main__':
    unittest.main()
