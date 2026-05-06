import unittest
from unittest.mock import MagicMock, patch
from app.services.retrieval import RetrievalService

class TestRetrievalLogic(unittest.TestCase):
    @patch('app.services.retrieval.Neo4jGraph')
    @patch('app.services.retrieval.GoogleGenerativeAIEmbeddings')
    @patch('app.services.retrieval.ChatGoogleGenerativeAI')
    def test_hybrid_search_logic(self, mock_llm, mock_embeddings, mock_graph):
        # Setup mocks
        mock_graph_instance = mock_graph.return_value
        mock_graph_instance.query.side_effect = [
            # First query (vector search)
            [{"text": "Alice is CEO of Acme", "score": 0.9, "node_id": 1}],
            # Second query (graph expansion)
            [{"relationship": "Alice WORKS_FOR Acme", "neighbor_id": 2}]
        ]
        
        mock_embeddings.return_value.embed_query.return_value = [0.1] * 768
        
        # Initialize service
        service = RetrievalService()
        
        # Run test
        result = service.hybrid_search("Who is Alice?")
        
        # Assertions
        self.assertIn("Alice is CEO of Acme", result['vector_context'])
        self.assertIn("Alice WORKS_FOR Acme", result['graph_context'])
        print("Logic Test Passed: Hybrid search correctly combines vector and graph data.")

if __name__ == "__main__":
    unittest.main()
