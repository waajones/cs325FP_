# similarity_calculator.py - Cosine similarity and recommendation ranking
# Calculates how similar resume is to each job using vector math
# Implements ISimilarityCalculator interface (DIP)

import numpy as np
from scipy.spatial.distance import cosine
from typing import List, Dict, Any, Optional
import logging
from interfaces import ISimilarityCalculator


class SimilarityCalculator(ISimilarityCalculator):
    
    # Initialize with logging
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.WARNING)
    
    # Calculate cosine similarity between two embedding vectors
    def calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        # Handle empty vectors
        if not vector1 or not vector2:
            return 0.0
        
        # Vectors must have same dimensions
        if len(vector1) != len(vector2):
            raise ValueError(f"Vector dimensions don't match: {len(vector1)} vs {len(vector2)}")
        
        try:
            # Convert to numpy arrays for math operations
            vec1 = np.array(vector1, dtype=np.float64)
            vec2 = np.array(vector2, dtype=np.float64)
            
            # Handle zero vectors
            if np.allclose(vec1, 0) or np.allclose(vec2, 0):
                return 0.0
            
            # Calculate cosine similarity (1 - cosine distance)
            similarity = 1 - cosine(vec1, vec2)
            
            # Clamp to valid range [0, 1]
            similarity = max(0.0, min(1.0, similarity))
            
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    # Calculate similarity between resume and all job embeddings
    def calculate_similarities(self, resume_embedding: List[float], 
                             job_embeddings: List[List[float]]) -> List[float]:
        if not resume_embedding:
            raise ValueError("Resume embedding cannot be empty")
        
        if not job_embeddings:
            return []
        
        similarities = []
        
        # Compare resume to each job
        for i, job_embedding in enumerate(job_embeddings):
            try:
                similarity = self.calculate_similarity(resume_embedding, job_embedding)
                similarities.append(similarity)
                
                # Log progress every 10 jobs
                if i % 10 == 0:
                    self.logger.info(f"Calculated similarity for job {i+1}/{len(job_embeddings)}")
                    
            except Exception as e:
                self.logger.error(f"Error calculating similarity for job {i}: {str(e)}")
                similarities.append(0.0)
        
        return similarities
    
    # Sort jobs by similarity and return top N recommendations
    def get_top_recommendations(self, jobs: List[Dict[Any, Any]], 
                               similarities: List[float], 
                               top_n: int = 10) -> List[Dict[Any, Any]]:
        # Validate input lengths match
        if len(jobs) != len(similarities):
            raise ValueError(f"Number of jobs ({len(jobs)}) doesn't match number of similarities ({len(similarities)})")
        
        if not jobs or not similarities:
            return []
        
        # Pair jobs with their similarity scores
        job_similarity_pairs = list(zip(jobs, similarities))
        
        # Sort by similarity (highest first)
        job_similarity_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Take top N
        top_pairs = job_similarity_pairs[:top_n]
        
        # Add similarity score to each job dict
        recommendations = []
        for job, similarity in top_pairs:
            recommendation = job.copy()
            recommendation['similarity'] = round(similarity, 4)
            recommendations.append(recommendation)
        
        self.logger.info(f"Generated top {len(recommendations)} recommendations")
        
        return recommendations
    
    # Calculate statistics (mean, median, std, etc.) for similarity scores
    def get_similarity_statistics(self, similarities: List[float]) -> Dict[str, float]:
        if not similarities:
            return {}
        
        similarities_array = np.array(similarities)
        
        # Calculate various statistics
        stats = {
            'count': len(similarities),
            'mean': float(np.mean(similarities_array)),
            'median': float(np.median(similarities_array)),
            'std': float(np.std(similarities_array)),
            'min': float(np.min(similarities_array)),
            'max': float(np.max(similarities_array)),
            'q25': float(np.percentile(similarities_array, 25)),
            'q75': float(np.percentile(similarities_array, 75))
        }
        
        return stats
    
    # Filter recommendations by minimum similarity or other criteria
    def filter_recommendations(self, recommendations: List[Dict[Any, Any]], 
                             min_similarity: float = 0.0,
                             location_filter: Optional[str] = None,
                             company_filter: Optional[str] = None) -> List[Dict[Any, Any]]:
        filtered = recommendations.copy()
        
        # Filter by minimum similarity score
        if min_similarity > 0:
            filtered = [rec for rec in filtered if rec.get('similarity', 0) >= min_similarity]
        
        # Filter by location (partial match)
        if location_filter:
            location_filter = location_filter.lower()
            filtered = [rec for rec in filtered 
                       if location_filter in rec.get('location', '').lower()]
        
        # Filter by company (partial match)
        if company_filter:
            company_filter = company_filter.lower()
            filtered = [rec for rec in filtered 
                       if company_filter in rec.get('company', '').lower()]
        
        self.logger.info(f"Filtered from {len(recommendations)} to {len(filtered)} recommendations")
        
        return filtered
    
    # Calculate similarity matrix between all embeddings (for clustering/analysis)
    def calculate_similarity_matrix(self, embeddings: List[List[float]]) -> np.ndarray:
        if not embeddings:
            return np.array([])
        
        n = len(embeddings)
        similarity_matrix = np.zeros((n, n))
        
        # Calculate pairwise similarities
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    sim = self.calculate_similarity(embeddings[i], embeddings[j])
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim
        
        return similarity_matrix
