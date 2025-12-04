# embedding_service.py - OpenAI embedding implementation
# Converts text into numerical vectors using OpenAI's API
# Implements IEmbeddingService interface (DIP)

import os
import time
import logging
from typing import List, Optional
from openai import OpenAI
from interfaces import IEmbeddingService


class OpenAIEmbeddingService(IEmbeddingService):
    
    # Initialize the service with API key and model settings
    def __init__(self, model: str = "text-embedding-3-small", api_key: Optional[str] = None):
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        # Create OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
        # Rate limiting settings (OpenAI allows 3000 requests/minute)
        self.requests_per_minute = 3000
        self.request_interval = 60.0 / self.requests_per_minute
        self.last_request_time = 0
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
    
    # Generate embedding for a single text with retry logic
    def get_embedding(self, text: str, max_retries: int = 3) -> List[float]:
        # Validate input text
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Truncate text if too long (OpenAI has token limits)
        max_tokens = 8000
        if len(text.split()) > max_tokens:
            text = ' '.join(text.split()[:max_tokens])
            self.logger.warning(f"Text truncated to {max_tokens} tokens")
        
        # Retry loop with exponential backoff
        for attempt in range(max_retries):
            try:
                # Wait if needed to respect rate limits
                self._wait_if_needed()

                # Call OpenAI API to generate embedding
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text,
                    encoding_format="float"
                )
                
                # Extract embedding vector from response
                embedding = response.data[0].embedding
                self.logger.debug(f"Successfully generated embedding (dimension: {len(embedding)})")
                return embedding
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                
                # Wait longer between retries (exponential backoff)
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 1.0
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed to generate embedding after {max_retries} attempts: {str(e)}")
        
        raise Exception("Unexpected error: embedding generation failed")
    
    # Generate embeddings for multiple texts in batches
    def get_embeddings_batch(self, texts: List[str], batch_size: int = 20) -> List[List[float]]:
        if not texts:
            return []
        
        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        # Process texts in batches for efficiency
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            
            self.logger.debug(f"Processing batch {batch_num}/{total_batches} ({len(batch)} texts)")
            
            try:
                self._wait_if_needed()
                
                # Prepare batch input (handle empty texts)
                batch_input = []
                for text in batch:
                    if not text or not text.strip():
                        batch_input.append("empty text")
                    else:
                        max_tokens = 8000
                        if len(text.split()) > max_tokens:
                            text = ' '.join(text.split()[:max_tokens])
                        batch_input.append(text)
                
                # Call OpenAI API with batch of texts
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch_input,
                    encoding_format="float"
                )
                
                # Extract all embeddings from response
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                self.logger.debug(f"Batch {batch_num} completed successfully")
                
                # Small delay between batches
                if i + batch_size < len(texts):
                    time.sleep(1.0)
                    
            except Exception as e:
                self.logger.error(f"Error processing batch {batch_num}: {str(e)}")
                all_embeddings.extend([None] * len(batch))
        
        return all_embeddings
    
    # Wait if needed to respect API rate limits
    def _wait_if_needed(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_interval:
            wait_time = self.request_interval - time_since_last
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    # Return information about the embedding model
    def get_embedding_info(self) -> dict:
        model_info = {
            "text-embedding-3-small": {"dimensions": 1536, "max_tokens": 8191},
            "text-embedding-3-large": {"dimensions": 3072, "max_tokens": 8191},
            "text-embedding-ada-002": {"dimensions": 1536, "max_tokens": 8191}
        }
        
        return {
            "model": self.model,
            "dimensions": model_info.get(self.model, {}).get("dimensions", "unknown"),
            "max_tokens": model_info.get(self.model, {}).get("max_tokens", "unknown"),
            "rate_limit": f"{self.requests_per_minute} requests per minute"
        }
    
    # Test API connection with a simple request
    def validate_api_connection(self) -> bool:
        try:
            test_embedding = self.get_embedding("test connection")
            return len(test_embedding) > 0
        except Exception as e:
            self.logger.error(f"API connection validation failed: {str(e)}")
            return False
