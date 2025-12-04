# job_scraper.py - Adzuna API job fetching implementation
# Fetches job postings from Adzuna (aggregates Indeed, Monster, etc.)
# Implements IJobScraper interface (DIP)

import os
import requests
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
from interfaces import IJobScraper


class AdzunaJobScraper(IJobScraper):
    
    # Initialize scraper with Adzuna API credentials
    def __init__(self, app_id: Optional[str] = None, api_key: Optional[str] = None):
        # Get API credentials from parameters or environment variables
        self.app_id = (app_id or os.environ.get('ADZUNA_APP_ID', '')).strip()
        self.api_key = (api_key or os.environ.get('ADZUNA_API_KEY', '')).strip()
        
        # Validate credentials are available
        if not self.app_id or not self.api_key:
            raise ValueError("ADZUNA_APP_ID and ADZUNA_API_KEY environment variables must be set")
        
        # Base URL for Adzuna API
        self.base_url = "https://api.adzuna.com/v1/api/jobs/us/search"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    # Fetch job postings from Adzuna API with pagination
    def scrape_jobs(self, location: str, keywords: str, max_jobs: int = 50,
                    progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        all_jobs = []
        page = 1
        results_per_page = 50
        
        try:
            # Keep fetching pages until we have enough jobs
            while len(all_jobs) < max_jobs:
                url = f"{self.base_url}/{page}"
                
                # Set up API request parameters
                params = {
                    'app_id': self.app_id,
                    'app_key': self.api_key,
                    'results_per_page': min(results_per_page, max_jobs - len(all_jobs)),
                    'what': keywords,
                    'where': location
                }
                
                self.logger.info(f"Fetching jobs from Adzuna API (page {page})...")
                
                # Make API request
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                # Parse JSON response
                data = response.json()
                results = data.get('results', [])
                
                # Stop if no more results
                if not results:
                    break
                
                # Convert each job to our standard format
                for job in results:
                    job_data = self._convert_adzuna_job(job)
                    if job_data:
                        all_jobs.append(job_data)
                
                # Report progress if callback provided
                if progress_callback:
                    progress_callback(len(all_jobs), max_jobs)
                
                # Stop if we got fewer results than requested (last page)
                if len(results) < results_per_page:
                    break
                
                page += 1
                
        except Exception as e:
            self.logger.error(f"Error fetching from Adzuna API: {str(e)}")
        
        return all_jobs[:max_jobs]
    
    # Convert Adzuna API response to our standard job format
    def _convert_adzuna_job(self, job: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            # Format salary range if available
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            salary = None
            if salary_min and salary_max:
                salary = f"${salary_min:,.0f} - ${salary_max:,.0f}"
            elif salary_min:
                salary = f"${salary_min:,.0f}+"

            # Get job type from contract fields
            contract_type = job.get('contract_type', 'full_time') 
            contract_time = job.get('contract_time', 'full_time')
            job_type = self._parse_job_type(contract_type, contract_time)
            
            # Return standardized job dictionary
            return {
                'title': job.get('title', 'N/A'),
                'company': job.get('company', {}).get('display_name', 'N/A'),
                'location': job.get('location', {}).get('display_name', 'N/A'),
                'description': job.get('description', ''),
                'salary': salary,
                'url': job.get('redirect_url'),
                'source': 'Adzuna (aggregates Indeed, Monster, etc.)',
                'posted_date': job.get('created', datetime.now().strftime('%Y-%m-%d')),
                'job_type': job_type
            }
        except Exception as e:
            self.logger.error(f"Error converting Adzuna job data: {str(e)}")
            return None
    
    # Normalize job type string from Adzuna format
    def _parse_job_type(self, contract_type: str, contract_time: str) -> str:
        # Map Adzuna job types to standard format
        type_map = {
            'full_time': 'Full-time',
            'part_time': 'Part-time',
            'contract': 'Contract',
            'temporary': 'Temporary',
            'permanent': 'Permanent',
            'internship': 'Internship'
        }
        
        # Try contract_type first, then contract_time, default to Full-time
        job_type = type_map.get(contract_type)
        if not job_type:
            job_type = type_map.get(contract_time, 'Full-time')
        
        return job_type
            