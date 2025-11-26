"""Tests for WikiKnowledgeSource."""

import tempfile
from pathlib import Path

import pytest

from agent.knowledge.wiki_source import WikiKnowledgeSource


@pytest.fixture
def temp_dir():
    """Create temporary directory for test."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_clone_repository(temp_dir):
    """Test cloning repository."""
    repo_url = "https://github.com/icoxfog417/personal-account-manager"
    knowledge_dir = "docs"
    local_path = temp_dir / "repo"
    
    wiki_source = WikiKnowledgeSource(repo_url, knowledge_dir, local_path)
    wiki_source.clone_or_update()
    
    assert local_path.exists()
    assert (local_path / ".git").exists()
    assert (local_path / knowledge_dir).exists()


def test_list_files(temp_dir):
    """Test listing files in knowledge directory."""
    repo_url = "https://github.com/icoxfog417/personal-account-manager"
    knowledge_dir = "docs"
    local_path = temp_dir / "repo"
    
    wiki_source = WikiKnowledgeSource(repo_url, knowledge_dir, local_path)
    wiki_source.clone_or_update()
    
    files = wiki_source.list_files()
    
    assert len(files) > 0
    assert all(isinstance(f, Path) for f in files)


def test_load_file(temp_dir):
    """Test loading file contents."""
    repo_url = "https://github.com/icoxfog417/personal-account-manager"
    knowledge_dir = "docs"
    local_path = temp_dir / "repo"
    
    wiki_source = WikiKnowledgeSource(repo_url, knowledge_dir, local_path)
    wiki_source.clone_or_update()
    
    files = wiki_source.list_files()
    assert len(files) > 0
    
    first_file = files[0]
    content = wiki_source.load_file(first_file)
    
    assert isinstance(content, str)
    assert len(content) > 0


def test_update_repository(temp_dir):
    """Test updating existing repository."""
    repo_url = "https://github.com/icoxfog417/personal-account-manager"
    knowledge_dir = "docs"
    local_path = temp_dir / "repo"
    
    wiki_source = WikiKnowledgeSource(repo_url, knowledge_dir, local_path)
    
    # First clone
    wiki_source.clone_or_update()
    assert local_path.exists()
    
    # Second call should update (pull)
    wiki_source.clone_or_update()
    assert local_path.exists()
    assert (local_path / ".git").exists()
