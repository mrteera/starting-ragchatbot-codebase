import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from typing import Dict, Any, List
from fastapi.testclient import TestClient

from config import Config
from rag_system import RAGSystem
from vector_store import VectorStore
from ai_generator import AIGenerator
from session_manager import SessionManager
from document_processor import DocumentProcessor


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def test_config(temp_data_dir):
    """Create a test configuration with temporary directories"""
    return Config(
        data_dir=temp_data_dir,
        chunk_size=200,
        chunk_overlap=50,
        max_results=3,
        max_history=2,
        embedding_model="all-MiniLM-L6-v2",
        anthropic_model="claude-sonnet-4-20250514",
        anthropic_api_key="test-key"
    )


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.content = [Mock(text="Test response")]
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing"""
    mock_store = Mock(spec=VectorStore)
    mock_store.search.return_value = [
        {"content": "Test content 1", "metadata": {"course": "Test Course", "lesson": "1"}},
        {"content": "Test content 2", "metadata": {"course": "Test Course", "lesson": "2"}}
    ]
    mock_store.get_existing_course_titles.return_value = ["Test Course", "Another Course"]
    mock_store.get_course_count.return_value = 2
    mock_store.add_course_metadata.return_value = None
    mock_store.add_course_content.return_value = None
    return mock_store


@pytest.fixture
def mock_ai_generator(mock_anthropic_client):
    """Mock AI generator for testing"""
    mock_generator = Mock(spec=AIGenerator)
    mock_generator.generate_response.return_value = ("Test answer", ["source1", "source2"])
    return mock_generator


@pytest.fixture
def mock_session_manager():
    """Mock session manager for testing"""
    mock_manager = Mock(spec=SessionManager)
    mock_manager.create_session.return_value = "test-session-123"
    mock_manager.add_message.return_value = None
    mock_manager.add_exchange.return_value = None
    mock_manager.get_conversation_history.return_value = None
    return mock_manager


@pytest.fixture
def mock_document_processor():
    """Mock document processor for testing"""
    mock_processor = Mock(spec=DocumentProcessor)
    
    # Mock Course object
    mock_course = Mock()
    mock_course.title = "Test Course"
    mock_course.course_link = "https://example.com/course"
    mock_course.instructor = "Test Instructor"
    mock_course.lessons = []
    
    # Mock CourseChunk objects
    mock_chunks = [
        Mock(content="Test chunk 1", course_title="Test Course", lesson_number=1, chunk_index=0),
        Mock(content="Test chunk 2", course_title="Test Course", lesson_number=2, chunk_index=1)
    ]
    
    mock_processor.process_course_document.return_value = (mock_course, mock_chunks)
    return mock_processor


@pytest.fixture
def mock_rag_system(mock_vector_store, mock_ai_generator, mock_session_manager, mock_document_processor):
    """Mock RAG system with all dependencies mocked"""
    mock_system = Mock(spec=RAGSystem)
    mock_system.query.return_value = ("Test answer", ["source1", "source2"])
    mock_system.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Test Course", "Another Course"]
    }
    mock_system.add_course_folder.return_value = (2, 4)  # courses, chunks
    mock_system.session_manager = mock_session_manager
    return mock_system


@pytest.fixture
def sample_course_data():
    """Sample course data for testing"""
    return {
        "course_content": """Course Title: Test Course
Course Link: https://example.com/course
Course Instructor: Test Instructor

Lesson 0: Introduction
Lesson Link: https://example.com/lesson0
This is the introduction to the test course.

Lesson 1: Basic Concepts
Lesson Link: https://example.com/lesson1
This lesson covers basic concepts and fundamentals.
""",
        "expected_chunks": [
            {"content": "Test Course Lesson 0: This is the introduction to the test course.", 
             "metadata": {"course": "Test Course", "lesson": "0"}},
            {"content": "Test Course Lesson 1: This lesson covers basic concepts and fundamentals.", 
             "metadata": {"course": "Test Course", "lesson": "1"}}
        ]
    }


@pytest.fixture
def sample_query_requests():
    """Sample API request data for testing"""
    return {
        "valid_query": {"query": "What is the course about?", "session_id": "test-session"},
        "query_without_session": {"query": "Tell me about lesson 1"},
        "empty_query": {"query": ""},
        "long_query": {"query": "a" * 1000}
    }


@pytest.fixture
def app_without_static_mount(mock_rag_system):
    """Create FastAPI app without static file mounting for testing"""
    from .test_app import create_test_app
    
    # Create test app with mocked RAG system
    return create_test_app(mock_rag_system)


@pytest.fixture
def test_client(app_without_static_mount):
    """Create test client with mocked dependencies"""
    return TestClient(app_without_static_mount)


@pytest.fixture
def temp_course_file(temp_data_dir, sample_course_data):
    """Create a temporary course file for testing"""
    course_file = os.path.join(temp_data_dir, "test_course.txt")
    with open(course_file, "w") as f:
        f.write(sample_course_data["course_content"])
    return course_file


@pytest.fixture
def temp_docs_folder(temp_data_dir, sample_course_data):
    """Create a temporary docs folder with sample courses"""
    docs_dir = os.path.join(temp_data_dir, "docs")
    os.makedirs(docs_dir)
    
    # Create multiple course files
    for i, course_name in enumerate(["Course_A", "Course_B"]):
        course_file = os.path.join(docs_dir, f"{course_name}.txt")
        content = sample_course_data["course_content"].replace("Test Course", course_name)
        with open(course_file, "w") as f:
            f.write(content)
    
    return docs_dir