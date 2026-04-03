"""Tests for agent memory service."""
import pytest
import tempfile
from neuralflow.services.agent_memory import AgentMemoryService


@pytest.fixture
def memory_service():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield AgentMemoryService(base_dir=tmpdir)


def test_add_memory(memory_service):
    entry = memory_service.add("agent-1", "Python is preferred for ML", "factual")
    assert entry.content == "Python is preferred for ML"
    assert entry.memory_type == "factual"
    assert entry.agent_id == "agent-1"


def test_search_all_memories(memory_service):
    memory_service.add("agent-1", "Python is great for ML", "factual")
    memory_service.add("agent-1", "Always test your code", "procedural")
    results = memory_service.search("agent-1")
    assert len(results) == 2


def test_search_by_type(memory_service):
    memory_service.add("agent-1", "Python is great for ML", "factual")
    memory_service.add("agent-1", "Always test your code", "procedural")
    results = memory_service.search("agent-1", memory_type="factual")
    assert len(results) == 1
    assert results[0].memory_type == "factual"


def test_search_by_query(memory_service):
    memory_service.add("agent-1", "Python is great for ML", "factual")
    memory_service.add("agent-1", "JavaScript is good for web", "factual")
    results = memory_service.search("agent-1", query="python")
    assert len(results) == 1
    assert "Python" in results[0].content


def test_delete_memory(memory_service):
    entry = memory_service.add("agent-1", "Test memory", "factual")
    assert memory_service.delete("agent-1", entry.id) is True
    results = memory_service.search("agent-1")
    assert len(results) == 0


def test_delete_nonexistent(memory_service):
    assert memory_service.delete("agent-1", "nonexistent") is False


def test_list_agents(memory_service):
    memory_service.add("agent-1", "Memory 1", "factual")
    memory_service.add("agent-2", "Memory 2", "factual")
    agents = memory_service.list_agents()
    assert "agent-1" in agents
    assert "agent-2" in agents


def test_get_stats(memory_service):
    memory_service.add("agent-1", "Memory 1", "factual")
    memory_service.add("agent-1", "Memory 2", "procedural")
    stats = memory_service.get_stats("agent-1")
    assert stats["total_memories"] == 2
    assert stats["by_type"]["factual"] == 1
    assert stats["by_type"]["procedural"] == 1
