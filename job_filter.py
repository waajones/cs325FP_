# job_filter.py - Job filtering by salary, experience, skills, etc.
# Filters job postings based on user-defined criteria
# Single Responsibility: Only handles filtering logic

import re
from typing import List, Dict, Optional


class JobFilter:
    
    # Main filter method - applies all filter criteria
    @staticmethod
    def filter_jobs(
        jobs: List[Dict],
        salary_min: int = 0,
        experience_levels: Optional[List[str]] = None,
        job_types: Optional[List[str]] = None,
        required_skills: Optional[List[str]] = None
    ) -> List[Dict]:
        filtered_jobs = jobs.copy()
        
        # Apply each filter if criteria provided
        if salary_min > 0:
            filtered_jobs = JobFilter._filter_by_salary(filtered_jobs, salary_min)
        
        if experience_levels and len(experience_levels) > 0:
            filtered_jobs = JobFilter._filter_by_experience(filtered_jobs, experience_levels)
        
        if job_types and len(job_types) > 0:
            filtered_jobs = JobFilter._filter_by_job_type(filtered_jobs, job_types)
        
        if required_skills and len(required_skills) > 0:
            filtered_jobs = JobFilter._filter_by_skills(filtered_jobs, required_skills)
        
        return filtered_jobs
    
    # Filter jobs by minimum salary threshold
    @staticmethod
    def _filter_by_salary(jobs: List[Dict], min_salary: int) -> List[Dict]:
        filtered = []
        
        for job in jobs:
            salary_str = job.get('salary', '')
            
            # Include jobs with no salary info (don't filter them out)
            if not salary_str or salary_str == 'N/A':
                filtered.append(job)
                continue
            
            # Extract salary numbers from string (e.g., "$100,000 - $150,000")
            salary_numbers = re.findall(r'\$?[\d,]+', salary_str)
            if salary_numbers:
                try:
                    # Use first number (minimum salary in range)
                    salary_value = int(salary_numbers[0].replace('$', '').replace(',', ''))
                    if salary_value >= min_salary:
                        filtered.append(job)
                except ValueError:
                    filtered.append(job)
            else:
                filtered.append(job)
        
        return filtered
    
    # Filter jobs by experience level (Senior, Junior, etc.)
    @staticmethod
    def _filter_by_experience(jobs: List[Dict], experience_levels: List[str]) -> List[Dict]:
        filtered = []
        
        # find patterns for each experience level
        level_patterns = {
            'Entry Level': r'(?i)\b(entry|junior|jr|graduate|intern)\b',
            'Junior': r'(?i)\b(junior|jr)\b',
            'Mid-Level': r'(?i)\b(mid|middle|intermediate)\b',
            'Senior': r'(?i)\b(senior|sr)\b',
            'Lead': r'(?i)\b(lead|principal|staff)\b',
            'Principal': r'(?i)\b(principal|staff|architect)\b',
            'Executive': r'(?i)\b(executive|director|vp|cto|ceo|head)\b'
        }
        
        for job in jobs:
            # Search in title and description
            text_to_search = f"{job.get('title', '')} {job.get('description', '')}"
            
            # Check if any requested level matches
            matched = False
            for level in experience_levels:
                if level in level_patterns:
                    if re.search(level_patterns[level], text_to_search):
                        matched = True
                        break
            
            if matched:
                filtered.append(job)
        
        return filtered
    
    # Filter jobs by job type (Full-time, Part-time, Contract, etc.)
    @staticmethod
    def _filter_by_job_type(jobs: List[Dict], job_types: List[str]) -> List[Dict]:
        filtered = []
        
        # Normalize job types to lowercase for comparison
        normalized_types = [jt.lower() for jt in job_types]
        
        for job in jobs:
            job_type = job.get('job_type', 'Full-time').lower()
            
            # Check job_type field first
            if any(nt in job_type for nt in normalized_types):
                filtered.append(job)
            else:
                # Also check title and description
                text = f"{job.get('title', '')} {job.get('description', '')}".lower()
                if any(nt in text for nt in normalized_types):
                    filtered.append(job)
        
        return filtered
    
    # Filter jobs that mention required skills
    @staticmethod
    def _filter_by_skills(jobs: List[Dict], required_skills: List[str]) -> List[Dict]:
        filtered = []
        
        # Normalize skills to lowercase
        normalized_skills = [skill.strip().lower() for skill in required_skills if skill.strip()]
        
        for job in jobs:
            # Search in title and description
            text_to_search = f"{job.get('title', '')} {job.get('description', '')}".lower()
            
            # Check if any required skill is mentioned
            skill_found = False
            for skill in normalized_skills:
                # Use word boundary to match whole words only
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_to_search):
                    skill_found = True
                    break
            
            if skill_found:
                filtered.append(job)
        
        return filtered
