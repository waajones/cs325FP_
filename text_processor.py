# text_processor.py - Text cleaning and preprocessing
# Cleans resume and job description text for embedding generation
# Implements ITextProcessor interface (DIP)

import re
import html
from typing import List, Optional
from interfaces import ITextProcessor


class TextProcessor(ITextProcessor):
    
    # Initialize with common stop words to optionally remove
    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their'
        }
    
    # Clean and normalize text for embedding generation
    def clean_text(self, text: str, remove_stop_words: bool = False) -> str:
        if not text or not isinstance(text, str):
            return ""
        
        # Decode HTML entities (&amp; -> &)
        text = html.unescape(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' ', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', ' ', text)
        text = re.sub(r'\(\d{3}\)\s*\d{3}[-.]?\d{4}', ' ', text)
        
        # Remove special characters (keep letters, numbers, spaces, basic punctuation)
        text = re.sub(r'[^\w\s.,!?;:()\-]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation
        text = re.sub(r'[.,!?;:]+', ' ', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Optionally remove stop words
        if remove_stop_words:
            words = text.split()
            words = [word for word in words if word not in self.stop_words and len(word) > 2]
            text = ' '.join(words)
        
        text = text.strip()
        
        return text
    
    # Extract sections (experience, education, skills) from resume text
    def extract_key_sections(self, resume_text: str) -> dict:
        sections = {
            'experience': '',
            'education': '',
            'skills': '',
            'summary': '',
            'full_text': resume_text
        }
        
        text_lower = resume_text.lower()
        
        # Patterns to identify section headers
        section_patterns = {
            'experience': r'(?:work\s+)?experience|employment|professional\s+experience',
            'education': r'education|academic|qualifications|degrees?',
            'skills': r'skills|technical\s+skills|competencies|technologies',
            'summary': r'summary|objective|profile|about'
        }
        
        # Find each section in the text
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text_lower)
            if match:
                start_pos = match.start()
                
                # Find where next section starts
                next_sections = []
                for other_pattern in section_patterns.values():
                    if other_pattern != pattern:
                        next_match = re.search(other_pattern, text_lower[start_pos + 100:])
                        if next_match:
                            next_sections.append(start_pos + 100 + next_match.start())
                
                # Extract section text
                if next_sections:
                    end_pos = min(next_sections)
                    sections[section_name] = resume_text[start_pos:end_pos].strip()
                else:
                    sections[section_name] = resume_text[start_pos:].strip()
        
        return sections
    
    # Combine job data fields into single text for embedding
    def prepare_job_text(self, job_data: dict) -> str:
        text_parts = []
        
        # Title is weighted more heavily (repeated)
        if job_data.get('title'):
            title = job_data['title']
            text_parts.extend([title] * 2)
        
        # Add company name
        if job_data.get('company'):
            text_parts.append(job_data['company'])
        
        # Add location
        if job_data.get('location'):
            text_parts.append(job_data['location'])
        
        # Add job description
        if job_data.get('description'):
            text_parts.append(job_data['description'])
        
        # Add salary info
        if job_data.get('salary'):
            text_parts.append(f"salary {job_data['salary']}")
        
        # Add job type
        if job_data.get('job_type'):
            text_parts.append(job_data['job_type'])
        
        # Combine and clean
        combined_text = ' '.join(text_parts)
        cleaned_text = self.clean_text(combined_text)
        
        return cleaned_text
    
    # Prepare resume text with optional focus on specific sections
    def prepare_resume_text(self, resume_text: str, focus_sections: Optional[List[str]] = None) -> str:
        if not focus_sections:
            focus_sections = ['experience', 'skills']
        
        # Extract sections from resume
        sections = self.extract_key_sections(resume_text)
        
        text_parts = []
        
        # Weight focus sections more heavily (repeated)
        for section in focus_sections:
            if sections.get(section):
                text_parts.extend([sections[section]] * 2)
        
        # Include full text as well
        text_parts.append(sections['full_text'])
        
        # Combine and clean
        combined_text = ' '.join(text_parts)
        cleaned_text = self.clean_text(combined_text)
        
        return cleaned_text
    
    # Normalize location strings for consistent matching
    def normalize_location(self, location: str) -> str:
        if not location:
            return ""
        
        location = location.lower().strip()
        
        # Common location variations to normalize
        normalizations = {
            'saint louis': 'st. louis',
            'st louis': 'st. louis',
            'saint paul': 'st. paul',
            'st paul': 'st. paul',
            'new york city': 'new york',
            'nyc': 'new york',
            'san francisco bay area': 'san francisco',
            'sf bay area': 'san francisco',
            'washington dc': 'washington',
            'washington d.c.': 'washington'
        }
        
        # Apply normalizations
        for old, new in normalizations.items():
            if old in location:
                location = location.replace(old, new)
        
        return location
