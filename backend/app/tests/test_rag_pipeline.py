
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.routers.retrieval import search_documents, SearchRequest, SearchResult
from app.models.document import Chunk
from app.models.user import User

# --- Mocks & Fixtures ---

@pytest.fixture
def mock_vector_store():
    with patch("app.routers.retrieval.vector_store") as mock:
        yield mock

@pytest.fixture
def mock_db_session():
    return AsyncMock()

@pytest.fixture
def mock_user():
    return User(id=1, email="test@example.com")

# --- Tests ---

@pytest.mark.asyncio
async def test_rag_ranking_logic(mock_vector_store, mock_db_session, mock_user):
    """
    Test that re-ranking correctly prioritizes chunks with higher feedback scores.
    """
    # 1. Mock Vector Store Results
    # Returning 2 hits with equal distance (0.5)
    mock_vector_store.query.return_value = {
        "ids": [["chunk_1", "chunk_2"]],
        "distances": [[0.5, 0.5]],
        "metadatas": [[{"some": "meta1"}, {"some": "meta2"}]],
        "documents": [["Text 1", "Text 2"]]
    }

    # 2. Mock Database Chunks
    # Chunk 1 has HIGH feedback (1.0) -> Score boost
    # Chunk 2 has LOW feedback (-1.0) -> Score penalty
    chunk1 = Chunk(embedding_id="chunk_1", text="Text 1", feedback_score=1.0, trust_score=0.5, summary="Sum1", generated_qas={})
    chunk2 = Chunk(embedding_id="chunk_2", text="Text 2", feedback_score=-1.0, trust_score=0.5, summary="Sum2", generated_qas={})
    
    # Mock the DB execution result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [chunk1, chunk2]
    mock_db_session.execute.return_value = mock_result

    # 3. Execute Search
    request = SearchRequest(query="test query")
    results = await search_documents(request, db=mock_db_session, current_user=mock_user)

    # 4. Verify Results
    assert len(results) == 2
    
    # Chunk 1 should be first because of positive feedback
    assert results[0].metadata["summary"] == "Sum1"
    assert results[0].score > results[1].score
    
    # Verify the specific score calculation logic if needed, 
    # but order is the most important invariant here.

@pytest.mark.asyncio
async def test_rag_enrichment(mock_vector_store, mock_db_session, mock_user):
    """
    Test that results are enriched with metadata (summary, QAs) from the database.
    """
    # 1. Mock Vector Store
    mock_vector_store.query.return_value = {
        "ids": [["chunk_enriched"]],
        "distances": [[0.2]], # Close match
        "metadatas": [[{}]],
        "documents": [["Raw text"]]
    }

    # 2. Mock DB
    db_chunk = Chunk(
        embedding_id="chunk_enriched", 
        text="Enriched Text from DB", 
        feedback_score=0.0,
        trust_score=0.8,
        summary="A great summary",
        generated_qas={"Q": "A"}
    )
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [db_chunk]
    mock_db_session.execute.return_value = mock_result

    # 3. Execute
    request = SearchRequest(query="metrics")
    results = await search_documents(request, db=mock_db_session, current_user=mock_user)

    # 4. Verify Content
    assert len(results) == 1
    res = results[0]
    
    # Should use text from DB logic
    assert res.text == "Enriched Text from DB"
    
    # Should contain enriched metadata
    assert res.metadata["summary"] == "A great summary"
    assert res.metadata["generated_qas"] == {"Q": "A"}
    assert res.metadata["trust_score"] == 0.8

@pytest.mark.asyncio
async def test_rag_fallback_on_db_miss(mock_vector_store, mock_db_session, mock_user):
    """
    Test fallback behavior when vector store returns an ID that is missing in the DB
    (e.g., sync lag). Should verify it doesn't crash and returns vector store data.
    """
    # 1. Mock Vector Store
    mock_vector_store.query.return_value = {
        "ids": [["chunk_missing_in_db"]],
        "distances": [[0.1]],
        "metadatas": [[{"original_meta": "preserved"}]],
        "documents": [["Fallback Text"]]
    }

    # 2. Mock DB returns EMPTY list
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db_session.execute.return_value = mock_result

    # 3. Execute
    request = SearchRequest(query="ghost")
    results = await search_documents(request, db=mock_db_session, current_user=mock_user)

    # 4. Verify Fallback
    assert len(results) == 1
    res = results[0]
    
    # Should fall back to vector store text and metadata
    assert res.text == "Fallback Text"
    assert res.metadata["original_meta"] == "preserved"
    # Score should still be calculated from distance
    assert res.score > 0
