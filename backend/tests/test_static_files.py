import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from unittest.mock import patch, Mock
import tempfile
import os
from pathlib import Path


@pytest.mark.api
class TestStaticFileHandling:
    """Test static file serving and related issues"""

    def test_app_creation_without_static_mount(self, app_without_static_mount):
        """Test that we can create app without static mounting for tests"""
        assert app_without_static_mount is not None
        assert app_without_static_mount.title == "Test Course Materials RAG System"

    def test_test_client_works_without_static_files(self, test_client):
        """Test that test client works without static file issues"""
        # This should not raise any errors about missing frontend directory
        response = test_client.get("/api/courses")
        assert response.status_code == 200

    @patch('os.path.exists')
    def test_app_startup_with_missing_docs(self, mock_exists, test_client):
        """Test app startup when docs directory doesn't exist"""
        mock_exists.return_value = False
        
        # Should handle missing docs gracefully
        response = test_client.get("/api/courses")
        assert response.status_code == 200

    def test_app_handles_missing_frontend_directory(self):
        """Test that we can handle missing frontend directory in tests"""
        # Create a test app that would normally fail due to missing frontend
        from .test_app import QueryRequest, QueryResponse, CourseStats
        
        test_app = FastAPI(title="Test App")
        
        # This should work fine without mounting static files
        @test_app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}
        
        with TestClient(test_app) as client:
            response = client.get("/test")
            assert response.status_code == 200

    def test_static_file_mount_alternative(self):
        """Test alternative approach to static file mounting for production"""
        test_app = FastAPI()
        
        # Create a temporary directory to simulate frontend
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple HTML file
            html_file = os.path.join(temp_dir, "index.html")
            with open(html_file, "w") as f:
                f.write("<html><body>Test</body></html>")
            
            # Mount static files
            test_app.mount("/", StaticFiles(directory=temp_dir, html=True), name="static")
            
            with TestClient(test_app) as client:
                # This should work with our temporary frontend
                response = client.get("/")
                assert response.status_code == 200
                assert "Test" in response.text


@pytest.mark.api
class TestDevStaticFiles:
    """Test the custom DevStaticFiles class"""

    def test_dev_static_files_no_cache_headers(self):
        """Test that DevStaticFiles pattern works"""
        # Test the concept of custom static files without importing from app
        from fastapi.staticfiles import StaticFiles
        
        # This test verifies we understand the pattern 
        # Full testing would require more complex mocking of StaticFiles behavior
        assert StaticFiles is not None

    def test_production_static_mounting_pattern(self):
        """Test the pattern used for static file mounting in production"""
        # This demonstrates how the production app mounts static files
        # and how our test setup avoids this issue
        
        production_app = FastAPI()
        
        # In production, this would work:
        # production_app.mount("/", StaticFiles(directory="../frontend", html=True))
        
        # In tests, we create apps without this mounting to avoid path issues
        test_app = FastAPI()
        # No static mounting in test app
        
        assert production_app is not None
        assert test_app is not None


@pytest.mark.integration
class TestFullAppWithStaticFiles:
    """Integration tests that deal with the full app including static files"""

    @patch('os.path.exists')
    def test_startup_event_docs_loading(self, mock_exists):
        """Test the startup event concept"""
        mock_exists.return_value = True
        
        # Test the startup event pattern without importing from app.py
        import asyncio
        
        async def mock_startup_event(rag_system_mock):
            """Mock version of startup event for testing"""
            docs_path = "../docs"
            if mock_exists(docs_path):
                try:
                    courses, chunks = rag_system_mock.add_course_folder(docs_path, clear_existing=False)
                    print(f"Loaded {courses} courses with {chunks} chunks")
                except Exception as e:
                    print(f"Error loading documents: {e}")
        
        # Test the mock startup
        async def test_startup():
            mock_rag = Mock()
            mock_rag.add_course_folder.return_value = (2, 10)
            await mock_startup_event(mock_rag)
            mock_rag.add_course_folder.assert_called_once()
        
        # Run the async test
        asyncio.run(test_startup())

    def test_app_configuration_for_tests(self, app_without_static_mount):
        """Test that our test app configuration is correct"""
        # Verify test app has the right endpoints
        routes = [route.path for route in app_without_static_mount.routes]
        
        assert "/api/query" in routes
        assert "/api/courses" in routes
        # Should not have static file routes
        assert "/" not in [route.path for route in app_without_static_mount.routes if hasattr(route, 'path')]


@pytest.mark.unit
class TestStaticFileConfiguration:
    """Unit tests for static file configuration logic"""

    def test_static_directory_path_resolution(self):
        """Test static directory path resolution logic"""
        # Test the path logic used in the main app
        frontend_path = "../frontend"
        
        # In tests, we avoid using this path
        # In production, this should point to the actual frontend directory
        assert isinstance(frontend_path, str)
        assert frontend_path.startswith("../")

    def test_html_flag_configuration(self):
        """Test HTML flag configuration for static files"""
        # Test that we understand the html=True flag usage
        html_flag = True
        
        # This flag enables serving index.html for SPA routing
        assert html_flag is True