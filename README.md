# Job Matcher - AI-Powered Job Recommendation Application
- A recommendation application that matches your resume to job postings using AI embeddings and cosine similarity. This project demonstrates the usage of SOLID principles, comprehensive unit testing, and professional documentation.

# Overview
- The Job Matcher analyzes your resume and compares it against job postings to find the best matches based on semantic similarity. It uses OpenAI's text embedding models to convert text into numerical vectors and calculates cosine similarity to rank job recommendations.

# Features
- Resume Parsing: Supports TXT, PDF, and DOCX file formats
- Job Aggregation: Fetches jobs from Adzuna API (aggregates Indeed, Monster, and 100+ job boards)
- AI-Powered Matching: Uses OpenAI embeddings for semantic similarity
- Smart Filtering: Filter by salary, experience level, job type, and required skills
- Detailed Output: Results saved in JSON and CSV formats
- Data Acquisition Strategy

Approach: Adzuna API Integration

Method: REST API calls to Adzuna job aggregation service

# Troubleshooting:
- Initially attempted direct web scraping from Indeed, Monster, and ZipRecruiter
- Encountered 403 Forbidden errors due to anti-bot protection (Cloudflare, bot detection)
- Tried cloudscraper and ScrapingAnt but still blocked by sophisticated protection
- Switched to Adzuna API which legally aggregates from 100+ job boards

# Technical Implementation:
- Endpoint: https://api.adzuna.com/v1/api/jobs/us/search/{page}
- Authentication: App ID and API Key (environment variables)
- Rate Limits: 1,000 API calls/month (free tier)
- Pagination: Page-based, up to 50 results per page
- Parameters: location, keywords, results per page

# How It Works
1. Parse Resume - Extracts text from your resume file
2. Scrape Jobs - Collects postings from Adzuna API (aggregates Indeed, Monster, etc)
3. Clean Text - Processes resume and job descriptions
4. Generate Embeddings - Uses OpenAI to create vectors
5. Calculate Similarity - Compares your resume to each job
6. Apply Filters - Filters by salary, experience, skills, etc.
7. Rank & Display - Shows top matching jobs that match your resume points

# Prerequisites
- Python 3.10 or higher
- OpenAI API key
- Adzuna API credentials (App ID and API Key)

# Installation
1. Clone the Repository
-git clone cd job-matcher

2. Create Virtual Environment (Optional but Recommended)
-python -m venv venv source venv/bin/activate

On Windows: venv\Scripts\activate

3. Install Dependencies
-python -m pip install -r requirements.txt

4. Configure Environment Variables
-Create a .env file in the project root:

OPENAI_API_KEY=your-openai-api-key-here ADZUNA_APP_ID=your-adzuna-app-id ADZUNA_API_KEY=your-adzuna-api-key

Getting API Keys:

OpenAI: Sign up at https://platform.openai.com and create an API key
Adzuna: Register at https://developer.adzuna.com to get App ID and API Key

# How to Use
In terminal:
python job_recommender.py [resume_name.pdf]
    -(Supports .pdf, .txt, or .docx files)


*Command Options*

Option              Description                         Default
resume	        Path to resume file (required)	           -
--location	    Job search location	                   St. Louis, MO
--keywords	    Job search keywords	                   software engineer
--max-jobs	    Maximum jobs to scrape	                   50
--min-salary	Minimum salary filter	                    0
--experience	Experience levels (space-separated)        All
--job-type	    Job types (space-separated)	               All
--skills	    Required skills (comma-separated)	       None
--top-n	        Number of recommendations	                10
--output	    CSV output file	                           None

Output Files
The system automatically saves outputs from each processing stage to the results/ directory:

Stage 1: Data Acquisition
job_postings_raw.json - Raw job data from Adzuna API
Stage 2: Data Preprocessing
resume_cleaned.txt - Cleaned resume text
job_cleaned.json - Cleaned job descriptions
Stage 3: Embeddings
resume_embedding.json - Resume vector embedding
job_embeddings.json - All job posting embeddings
Stage 4: Similarity & Ranking
similarity_scores.json - Similarity scores for all jobs
top_recommendations.json - Top recommendations (JSON format)
top_recommendations.csv - Top recommendations (CSV format)

Examples of using with parameters:

python job_recommender.py resume.pdf--location "San Francisco, CA" --keywords "python developer" --max-jobs 100

python job_recommender.py resume.pdf --min-salary 100000 --experience Senior Lead --skills "Python, AWS, Docker"

python job_recommender.py resume.pdf --output my_recommendations.csv

# Running Tests
* Run all tests: python -m pytest tests/ -v

* Run specific test file: python -m pytest tests/test_embedding_service.py -v

* Run tests with standard unittest: python -m unittest discover tests -v

# Using Docker
* Build Docker Image: docker build -t job-matcher .
* Run with Docker: docker run --env-file .env -v $(pwd)/resume.pdf:/app/resume.pdf job-matcher resume.pdf

# SOLID Principles
This project implements two key SOLID principles:

Single Responsibility Principle (SRP); Each class has a single responsibility:
- OpenAIEmbeddingService: Generate text embeddings
- AdzunaJobScraper: Fetch jobs from API
- ResumeParser: Parse resume files
- TextProcessor: Clean and preprocess text
- SimilarityCalculator: Calculate similarity scores
- JobFilter: Filter jobs based on criteria

Dependency Inversion Principle (DIP); High-level modules depend on abstractions:
- All services implement interfaces (e.g., IEmbeddingService)
- JobRecommendationService accepts dependencies through constructor injection
- This enables easy testing with mock implementations

See REFACTORING.md for detailed documentation."
