# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Quick start (recommended)
chmod +x run.sh && ./run.sh

# Manual start 
cd backend && uv run uvicorn app:app --reload --port 8000
```

### Package Management
```bash
# Install/sync dependencies
uv sync

# Add new dependency
uv add package_name

# Run Python commands
uv run python script.py
```

### Environment Setup
Create `.env` file in root with:
```
ANTHROPIC_API_KEY=your_api_key_here
```

### Code Quality Tools
```bash
# Format code with black and isort
./scripts/format.sh
uv run black .
uv run isort .

# Run linting checks
./scripts/lint.sh
uv run flake8 .
uv run mypy .

# Run all quality checks (format + lint)
./scripts/quality.sh
```

## Architecture Overview

This is a **Course Materials RAG System** using tool-based search rather than traditional retrieve-then-generate patterns.

### Core Processing Flow
1. **Document Ingestion**: `DocumentProcessor` parses structured course files with metadata headers and lesson markers
2. **Vector Storage**: Text chunks stored in ChromaDB with course/lesson context embedded in content
3. **Tool-Based Search**: Claude decides when to use `CourseSearchTool` for semantic search
4. **Response Generation**: AI synthesizes search results into educational responses

### Key Architecture Decisions

**Tool-Calling RAG**: Instead of always retrieving context, Claude uses tools only when needed for course-specific queries. The `CourseSearchTool` provides structured search with course name resolution and lesson filtering.

**Contextual Chunking**: Text chunks include course and lesson identifiers in their content (e.g., "Course Title Lesson X content: ...") to maintain context during vector similarity search.

**Session Management**: Conversation history is maintained per session with configurable limits (`MAX_HISTORY=2`) to provide context without excessive token usage.

**Structured Document Format**: Course documents follow a specific format:
```
Course Title: [title]
Course Link: [url]
Course Instructor: [instructor]

Lesson 0: Introduction
Lesson Link: [lesson_url]
[content...]
```

### Component Interactions

**RAGSystem** (`rag_system.py`) orchestrates between:
- `DocumentProcessor`: Handles file parsing and chunking
- `VectorStore`: ChromaDB interface with semantic search
- `AIGenerator`: Claude API integration with tool support
- `SessionManager`: Conversation history tracking
- `ToolManager`: Registers and executes search tools

**Search Resolution**: `VectorStore.search()` performs fuzzy course name matching before content search, allowing partial matches like "MCP" → "MCP: Build Rich-Context AI Apps with Anthropic".

### Configuration

All settings centralized in `config.py`:
- `CHUNK_SIZE=800, CHUNK_OVERLAP=100`: Text processing parameters
- `MAX_RESULTS=5`: Vector search limit
- `EMBEDDING_MODEL="all-MiniLM-L6-v2"`: Sentence transformer model
- `ANTHROPIC_MODEL="claude-sonnet-4-20250514"`: AI model version

### API Structure

FastAPI server (`app.py`) provides:
- `POST /api/query`: Main chat endpoint returning `{answer, sources, session_id}`
- `GET /api/courses`: Course analytics endpoint
- Static file serving for frontend at root `/`

Frontend is a simple HTML/JS interface that maintains session state and displays sources in collapsible sections.

### Data Flow

Documents → Chunking → Vector Storage → Tool-based Search → AI Generation → Response

The system processes course documents into searchable chunks, then uses Claude's tool-calling capabilities to perform semantic search only when course-specific information is needed, maintaining conversation context throughout the interaction.