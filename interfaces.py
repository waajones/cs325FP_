# interfaces.py - Abstract interfaces for Dependency Inversion Principle (DIP)
# These interfaces define contracts that concrete classes must implement
# High-level modules depend on these abstractions, not concrete implementations

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


# Interface for embedding services (OpenAI, Gemini, etc.)
class IEmbeddingService(ABC):
    
    # Convert text to a numerical vector (embedding)
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        pass
    
    # Convert multiple texts to vectors in batches for efficiency
    @abstractmethod
    def get_embeddings_batch(self, texts: List[str], batch_size: int = 20) -> List[List[float]]:
        pass
    
    # Return info about the embedding model (dimensions, limits, etc.)
    @abstractmethod
    def get_embedding_info(self) -> dict:
        pass


# Interface for job scraping services (Adzuna, Indeed, LinkedIn, etc.)
class IJobScraper(ABC):
    
    # Fetch job postings from an external API or website
    @abstractmethod
    def scrape_jobs(self, location: str, keywords: str, max_jobs: int = 50,
                    progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        pass


# Interface for resume parsing services
class IResumeParser(ABC):
    
    # Extract text content from resume files (PDF, DOCX, TXT)
    @abstractmethod
    def parse_file(self, file_path: str) -> Optional[str]:
        pass


# Interface for text processing services
class ITextProcessor(ABC):
    
    # Clean and preprocess text (remove HTML, URLs, normalize whitespace)
    @abstractmethod
    def clean_text(self, text: str, remove_stop_words: bool = False) -> str:
        pass


# Abstract class for similarity calculation services
class ISimilarityCalculator(ABC):
    
    # Calculate cosine similarity between two vectors (0 to 1)
    @abstractmethod
    def calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        pass
    
    # Calculate similarity between resume and all job embeddings
    @abstractmethod
    def calculate_similarities(self, resume_embedding: List[float],
                               job_embeddings: List[List[float]]) -> List[float]:
        pass
    
    # Sort jobs by similarity and return top N recommendations
    @abstractmethod
    def get_top_recommendations(self, jobs: List[Dict[Any, Any]],
                                similarities: List[float],
                                top_n: int = 10) -> List[Dict[Any, Any]]:
        pass
