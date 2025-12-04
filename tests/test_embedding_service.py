"""
Unit tests for the EmbeddingService module.

Demonstrates testing classes that use external APIs by using mock implementations.
This is possible because of DIP - we depend on the IEmbeddingService interface,
not the concrete implementation.
"""

import unittest
from unittest.mock import patch
from typing import List

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interfaces import IEmbeddingService
from embedding_service import OpenAIEmbeddingService


class MockEmbeddingService(IEmbeddingService):
    """
    Mock implementation of IEmbeddingService for testing.
    
    This demonstrates DIP - we can create a mock that doesn't make real API calls
    but follows the same interface contract.
    """
    
    def __init__(self, embedding_dimension: int = 1536):
        self.embedding_dimension = embedding_dimension
        self.call_count = 0
    
    def get_embedding(self, text: str) -> List[float]:
        """Return a deterministic fake embedding based on text length."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        self.call_count += 1
        fake_value = float(len(text) % 10) / 10.0
        return [fake_value] * self.embedding_dimension
    
    def get_embeddings_batch(self, texts: List[str], batch_size: int = 20) -> List[List[float]]:
        """Return fake embeddings for a batch of texts."""
        if not texts:
            return []
        return [self.get_embedding(text) for text in texts]
    
    def get_embedding_info(self) -> dict:
        """Return mock model information."""
        return {"model": "mock-embedding", "dimensions": self.embedding_dimension}


class TestMockEmbeddingService(unittest.TestCase):
    """Test the MockEmbeddingService implementation."""
    
    def setUp(self):
        """Create a fresh mock for each test."""
        self.mock_service = MockEmbeddingService()
    
    def test_get_embedding_returns_correct_dimension(self):
        """Test that embeddings have the correct dimension (1536 like OpenAI)."""
        embedding = self.mock_service.get_embedding("test text")
        self.assertEqual(len(embedding), 1536)
    
    def test_get_embedding_raises_on_empty_text(self):
        """Test that empty text raises ValueError."""
        with self.assertRaises(ValueError):
            self.mock_service.get_embedding("")
    
    def test_get_embeddings_batch_returns_correct_count(self):
        """Test that batch returns one embedding per input text."""
        texts = ["text one", "text two", "text three"]
        embeddings = self.mock_service.get_embeddings_batch(texts)
        self.assertEqual(len(embeddings), 3)


class TestOpenAIEmbeddingService(unittest.TestCase):
    """Test the OpenAIEmbeddingService implementation."""
    
    def test_init_raises_without_api_key(self):
        """Test that missing API key raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('OPENAI_API_KEY', None)
            with self.assertRaises(ValueError):
                OpenAIEmbeddingService()
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"})
    def test_init_with_api_key(self):
        """Test successful initialization with API key."""
        service = OpenAIEmbeddingService()
        self.assertIsNotNone(service.client)


class TestEmbeddingServiceInterface(unittest.TestCase):
    """Test that implementations follow the interface contract."""
    
    def test_mock_implements_interface(self):
        """Verify MockEmbeddingService implements IEmbeddingService."""
        mock = MockEmbeddingService()
        self.assertIsInstance(mock, IEmbeddingService)


if __name__ == '__main__':
    unittest.main()
