"""Integration tests for SupportAgent."""

from pathlib import Path
from unittest.mock import patch

import pytest

from agent.support_agent import SupportAgent


@pytest.fixture
def agent():
    """Create SupportAgent with actual repository."""
    # Use the actual repository that's already cloned
    return SupportAgent(
        repo_url="https://github.com/icoxfog417/personal-account-manager",
        knowledge_dir="docs",
        local_path="./repo_data"
    )


class TestSupportAgentIntegration:
    """Integration tests for SupportAgent with actual repository."""

    def test_agent_initializes_successfully(self, agent):
        """Test that agent initializes with all components."""
        assert agent.wiki_source is not None
        assert agent.support_tools is not None

    def test_agent_responds_to_question(self, agent):
        """Test that agent uses repository knowledge to answer."""
        response = agent("Tell me about GenU")

        # Agent should use search_wiki tool and find content
        response_str = str(response)
        assert len(response_str) > 0

    def test_agent_handles_unknown_topic(self, agent):
        """Test that agent handles questions about unknown topics."""
        response = agent("What is xyz123nonexistent?")

        assert response is not None

    def test_search_knowledge_returns_results(self, agent):
        """Test that search_knowledge finds content in repository."""
        result = agent.search_knowledge("GenU")

        assert isinstance(result, str)
        assert len(result) > 0

    def test_search_knowledge_handles_no_match(self, agent):
        """Test that search_knowledge handles queries with no matches."""
        result = agent.search_knowledge("nonexistent_keyword_xyz123")

        assert "No relevant content found" in result

    def test_tools_are_accessible(self, agent):
        """Test that agent has access to search and list tools."""
        # Verify tools exist
        assert hasattr(agent.support_tools, 'search_wiki')
        assert hasattr(agent.support_tools, 'list_wiki_files')

    def test_list_files_returns_documentation(self, agent):
        """Test that list_wiki_files returns actual files."""
        result = agent.support_tools.list_wiki_files()

        assert "Available wiki files:" in result
        assert ".md" in result

