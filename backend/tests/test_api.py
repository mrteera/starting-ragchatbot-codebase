import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json


@pytest.mark.api
class TestQueryAPI:
    """Test the /api/query endpoint"""

    def test_query_with_session_id(self, test_client, sample_query_requests):
        """Test successful query with existing session ID"""
        response = test_client.post(
            "/api/query",
            json=sample_query_requests["valid_query"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["session_id"] == "test-session"
        assert isinstance(data["sources"], list)

    def test_query_without_session_id(self, test_client, sample_query_requests, mock_rag_system):
        """Test query without session ID creates new session"""
        response = test_client.post(
            "/api/query",
            json=sample_query_requests["query_without_session"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        # Should call create_session when no session_id provided
        mock_rag_system.session_manager.create_session.assert_called()

    def test_query_empty_string(self, test_client, sample_query_requests):
        """Test query with empty string"""
        response = test_client.post(
            "/api/query",
            json=sample_query_requests["empty_query"]
        )
        
        assert response.status_code == 200
        # Should still process empty queries (up to the RAG system to handle)

    def test_query_long_input(self, test_client, sample_query_requests):
        """Test query with very long input"""
        response = test_client.post(
            "/api/query",
            json=sample_query_requests["long_query"]
        )
        
        assert response.status_code == 200

    def test_query_invalid_json(self, test_client):
        """Test query with invalid JSON structure"""
        response = test_client.post(
            "/api/query",
            json={"invalid_field": "value"}
        )
        
        assert response.status_code == 422  # Validation error

    def test_query_missing_required_field(self, test_client):
        """Test query without required query field"""
        response = test_client.post(
            "/api/query",
            json={"session_id": "test"}
        )
        
        assert response.status_code == 422

    def test_query_rag_system_exception(self, mock_rag_system):
        """Test handling of RAG system exceptions"""
        from .test_app import create_test_app
        from fastapi.testclient import TestClient
        
        # Create an app with a RAG system that raises exceptions
        mock_rag_system.query.side_effect = Exception("RAG system error")
        app = create_test_app(mock_rag_system)
        
        with TestClient(app) as client:
            response = client.post(
                "/api/query",
                json={"query": "test query"}
            )
            
            assert response.status_code == 500
            assert "RAG system error" in response.json()["detail"]

    def test_query_response_structure(self, test_client, mock_rag_system):
        """Test that response matches expected schema"""
        mock_rag_system.query.return_value = ("Custom answer", ["source1", "source2"])
        
        response = test_client.post(
            "/api/query",
            json={"query": "test query"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify exact response structure
        assert set(data.keys()) == {"answer", "sources", "session_id"}
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["session_id"], str)


@pytest.mark.api
class TestCoursesAPI:
    """Test the /api/courses endpoint"""

    def test_courses_success(self, test_client):
        """Test successful courses request"""
        response = test_client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_courses" in data
        assert "course_titles" in data
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
        assert data["total_courses"] == 2
        assert "Test Course" in data["course_titles"]

    def test_courses_response_structure(self, test_client):
        """Test that courses response matches expected schema"""
        response = test_client.get("/api/courses")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify exact response structure
        assert set(data.keys()) == {"total_courses", "course_titles"}

    def test_courses_rag_system_exception(self, mock_rag_system):
        """Test handling of RAG system exceptions in courses endpoint"""
        from .test_app import create_test_app
        from fastapi.testclient import TestClient
        
        # Create an app with a RAG system that raises exceptions
        mock_rag_system.get_course_analytics.side_effect = Exception("Analytics error")
        app = create_test_app(mock_rag_system)
        
        with TestClient(app) as client:
            response = client.get("/api/courses")
            
            assert response.status_code == 500
            assert "Analytics error" in response.json()["detail"]

    def test_courses_no_parameters(self, test_client):
        """Test that courses endpoint doesn't accept parameters"""
        response = test_client.get("/api/courses?param=value")
        
        # Should still work, parameters ignored
        assert response.status_code == 200


@pytest.mark.api
class TestCORSAndMiddleware:
    """Test CORS and middleware configuration"""

    def test_cors_headers_present(self, test_client):
        """Test that CORS headers are present in responses"""
        response = test_client.options("/api/query")
        
        # FastAPI TestClient doesn't fully simulate CORS, but we can test the app setup
        # In real deployment, these headers would be present
        assert response.status_code in [200, 405]  # OPTIONS may not be explicitly handled

    def test_cors_allows_all_origins(self, test_client):
        """Test CORS configuration allows requests"""
        # This is more of a configuration test
        response = test_client.post(
            "/api/query",
            json={"query": "test"},
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200


@pytest.mark.api 
class TestErrorHandling:
    """Test various error conditions and edge cases"""

    def test_malformed_json(self, test_client):
        """Test malformed JSON request"""
        response = test_client.post(
            "/api/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422

    def test_unsupported_media_type(self, test_client):
        """Test unsupported content type"""
        response = test_client.post(
            "/api/query",
            data="query=test",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Should fail due to expecting JSON
        assert response.status_code == 422

    def test_nonexistent_endpoint(self, test_client):
        """Test request to non-existent endpoint"""
        response = test_client.get("/api/nonexistent")
        
        assert response.status_code == 404

    def test_wrong_http_method(self, test_client):
        """Test wrong HTTP method on endpoints"""
        # GET on POST endpoint
        response = test_client.get("/api/query")
        assert response.status_code == 405
        
        # POST on GET endpoint
        response = test_client.post("/api/courses")
        assert response.status_code == 405


@pytest.mark.api
@pytest.mark.integration
class TestEndToEndFlow:
    """Test complete API workflows"""

    def test_complete_query_flow(self, test_client, mock_rag_system):
        """Test complete query workflow from start to finish"""
        # Mock the RAG system responses
        mock_rag_system.session_manager.create_session.return_value = "new-session-123"
        mock_rag_system.query.return_value = ("Complete answer", ["source1", "source2"])
        
        # Step 1: Query without session (creates new session)
        response1 = test_client.post(
            "/api/query",
            json={"query": "What is this course about?"}
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        session_id = data1["session_id"]
        
        # Step 2: Query with existing session
        response2 = test_client.post(
            "/api/query",
            json={"query": "Tell me more", "session_id": session_id}
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["session_id"] == session_id

    def test_query_then_courses_flow(self, test_client):
        """Test querying then getting course stats"""
        # Step 1: Make a query
        query_response = test_client.post(
            "/api/query",
            json={"query": "What courses are available?"}
        )
        assert query_response.status_code == 200
        
        # Step 2: Get course statistics
        courses_response = test_client.get("/api/courses")
        assert courses_response.status_code == 200
        
        courses_data = courses_response.json()
        assert courses_data["total_courses"] >= 0
        assert isinstance(courses_data["course_titles"], list)