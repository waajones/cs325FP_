#!/usr/bin/env python3
# job_recommender.py - Main entry point and CLI for Job Matcher
# Orchestrates the complete job recommendation pipeline
# Demonstrates SOLID principles (SRP and DIP)

from dotenv import load_dotenv
load_dotenv()
import os
import sys
import argparse
import json
from datetime import datetime
import pandas as pd

from interfaces import IEmbeddingService, IJobScraper, IResumeParser, ITextProcessor, ISimilarityCalculator
from job_scraper import AdzunaJobScraper
from resume_parser import ResumeParser
from text_processor import TextProcessor
from embedding_service import OpenAIEmbeddingService
from similarity_calculator import SimilarityCalculator
from job_filter import JobFilter


# Save output to results directory for debugging and analysis
def save_stage_output(filename, data, mode='json'):
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    filepath = os.path.join('results', filename)
    
    # Save as JSON or plain text
    if mode == 'json':
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    elif mode == 'txt':
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
    
    return filepath


# Main service class - orchestrates the recommendation pipeline
# Demonstrates DIP: depends on interfaces, not concrete implementations
class JobRecommendationService:
    
    # Initialize with injected dependencies (all interfaces, not concrete classes)
    def __init__(
        self,
        job_scraper: IJobScraper,
        resume_parser: IResumeParser,
        text_processor: ITextProcessor,
        embedding_service: IEmbeddingService,
        similarity_calculator: ISimilarityCalculator
    ):
        self.job_scraper = job_scraper
        self.resume_parser = resume_parser
        self.text_processor = text_processor
        self.embedding_service = embedding_service
        self.similarity_calculator = similarity_calculator
    
    # Main method - run the complete recommendation pipeline
    def get_recommendations(
        self,
        resume_path: str,
        location: str = "St. Louis, MO",
        keywords: str = "software engineer",
        max_jobs: int = 50,
        top_n: int = 10,
        filters: dict = None
    ) -> list:
        # Step 1: Parse the resume file
        print("Step 1: Processing resume...")
        resume_text = self.resume_parser.parse_file(resume_path)
        if not resume_text:
            raise ValueError("Failed to extract text from resume")
        print(f"   SUCCESS: Resume processed ({len(resume_text)} characters)")
        
        # Step 2: Fetch jobs from Adzuna API
        print("\nStep 2: Scraping job postings...")
        jobs = self.job_scraper.scrape_jobs(
            location=location,
            keywords=keywords,
            max_jobs=max_jobs
        )
        if not jobs:
            raise ValueError("No jobs found")
        print(f"   SUCCESS: Scraped {len(jobs)} job postings")
        
        # Save raw job data for debugging
        save_stage_output('job_postings_raw.json', jobs)
        
        # Step 3: Apply filters if provided
        if filters:
            print("\nStep 3: Applying filters...")
            jobs = JobFilter.filter_jobs(
                jobs=jobs,
                salary_min=filters.get('salary_min', 0),
                experience_levels=filters.get('experience_levels', []),
                job_types=filters.get('job_types', []),
                required_skills=filters.get('required_skills', [])
            )
            if not jobs:
                raise ValueError("No jobs match filter criteria")
            print(f"   SUCCESS: {len(jobs)} jobs match filters")
        
        # Step 4: Generate embeddings for resume and jobs
        print("\nStep 4: Generating embeddings...")
        
        # Clean and embed resume
        clean_resume = self.text_processor.clean_text(resume_text)
        resume_embedding = self.embedding_service.get_embedding(clean_resume)
        
        # Clean all job descriptions
        job_texts = []
        for job in jobs:
            clean_desc = self.text_processor.clean_text(job.get('description', ''))
            job_texts.append(clean_desc)
        
        # Save cleaned resume
        save_stage_output('resume_cleaned.txt', clean_resume, mode='txt')
        
        # Generate embeddings for all jobs in batches
        job_embeddings = self.embedding_service.get_embeddings_batch(job_texts, batch_size=20)
        if not job_embeddings or None in job_embeddings:
            raise ValueError("Failed to generate embeddings")
        print(f"   SUCCESS: Generated {len(job_embeddings)} job embeddings")
        
        # Save embeddings for debugging
        save_stage_output('resume_embedding.json', {
            'embedding': resume_embedding,
            'dimension': len(resume_embedding)
        })
        save_stage_output('job_embeddings.json', {
            'embeddings': job_embeddings,
            'count': len(job_embeddings),
            'dimension': len(job_embeddings[0]) if job_embeddings else 0
        })
        
        # Step 5: Calculate similarities and rank recommendations
        print("\nStep 5: Calculating similarities...")
        similarities = self.similarity_calculator.calculate_similarities(
            resume_embedding, job_embeddings
        )
        recommendations = self.similarity_calculator.get_top_recommendations(
            jobs, similarities, top_n=top_n
        )
        print(f"   SUCCESS: Found top {len(recommendations)} recommendations")
        
        # Save all similarity scores
        all_similarity_scores = []
        for i, (job, score) in enumerate(zip(jobs, similarities)):
            all_similarity_scores.append({
                'rank': i + 1,
                'title': job.get('title'),
                'company': job.get('company'),
                'location': job.get('location'),
                'similarity_score': float(score)
            })
        
        save_stage_output('similarity_scores.json', all_similarity_scores)
        save_stage_output('top_recommendations.json', recommendations)
        
        # Save as CSV for easy viewing
        df_top = pd.DataFrame(recommendations)
        df_top.to_csv(os.path.join('results', 'top_recommendations.csv'), index=False)
        
        return recommendations


# Factory function - creates service with default implementations
# Easy to swap implementations by changing this function
def create_default_service() -> JobRecommendationService:
    return JobRecommendationService(
        job_scraper=AdzunaJobScraper(),
        resume_parser=ResumeParser(),
        text_processor=TextProcessor(),
        embedding_service=OpenAIEmbeddingService(),
        similarity_calculator=SimilarityCalculator()
    )


# Main entry point - parse arguments and run pipeline
def main():
    # Set up command line argument parser
    parser = argparse.ArgumentParser(
        description='Find job recommendations based on your resume using AI-powered similarity matching'
    )
    
    # Required argument: resume file path
    parser.add_argument('resume', help='Path to your resume file (TXT, PDF, or DOCX)')
    
    # Optional search parameters
    parser.add_argument('--location', default='St. Louis, MO', help='Job location (default: St. Louis, MO)')
    parser.add_argument('--keywords', default='software engineer', help='Job keywords (default: software engineer)')
    parser.add_argument('--max-jobs', type=int, default=50, help='Maximum jobs to scrape (default: 50)')
    
    # Optional filter parameters
    parser.add_argument('--min-salary', type=int, default=0, help='Minimum salary filter')
    parser.add_argument('--experience', nargs='+', choices=['Entry Level', 'Junior', 'Mid-Level', 'Senior', 'Lead', 'Principal', 'Executive'], 
                       help='Experience levels to filter')
    parser.add_argument('--job-type', nargs='+', choices=['Full-time', 'Part-time', 'Contract', 'Temporary', 'Internship', 'Permanent'],
                       help='Job types to filter')
    parser.add_argument('--skills', help='Required skills (comma-separated)')
    
    # Output options
    parser.add_argument('--top-n', type=int, default=10, help='Number of recommendations to show (default: 10)')
    parser.add_argument('--output', help='Save recommendations to CSV file')
    
    args = parser.parse_args()
    
    # Validate resume file exists
    if not os.path.exists(args.resume):
        print(f"Error: Resume file '{args.resume}' not found")
        sys.exit(1)
    
    # Validate API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Print header
    print("=" * 70)
    print("JOB RECOMMENDATION SYSTEM")
    print("=" * 70)
    print()
    
    try:
        # Create service with default implementations
        service = create_default_service()
        
        # Build filters dict if any filter options provided
        filters = None
        if args.min_salary or args.experience or args.job_type or args.skills:
            skills_list = []
            if args.skills:
                skills_list = [s.strip() for s in args.skills.split(',')]
            
            filters = {
                'salary_min': args.min_salary,
                'experience_levels': args.experience or [],
                'job_types': args.job_type or [],
                'required_skills': skills_list
            }
        
        # Run the recommendation pipeline
        recommendations = service.get_recommendations(
            resume_path=args.resume,
            location=args.location,
            keywords=args.keywords,
            max_jobs=args.max_jobs,
            top_n=args.top_n,
            filters=filters
        )
        
        # Display results
        print()
        print("=" * 70)
        print(f"TOP {len(recommendations)} JOB RECOMMENDATIONS")
        print("=" * 70)
        print()
        
        # Print each recommendation
        for i, rec in enumerate(recommendations, 1):
            print(f"#{i} - {rec['title']}")
            print(f"    Company: {rec['company']}")
            print(f"    Location: {rec['location']}")
            print(f"    Similarity Score: {rec['similarity']:.3f}")
            
            if rec.get('salary'):
                print(f"    Salary: {rec['salary']}")
            
            if rec.get('job_type'):
                print(f"    Job Type: {rec['job_type']}")
            
            if rec.get('url'):
                print(f"    URL: {rec['url']}")
            
            print()
        
        # Save to CSV if output file specified
        if args.output:
            df = pd.DataFrame(recommendations)
            df.to_csv(args.output, index=False)
            print(f"Recommendations saved to: {args.output}")
            print()
        
        print("=" * 70)
        print("Job recommendation process complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
