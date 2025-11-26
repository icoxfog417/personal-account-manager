"""SupportAgent - AWS Customer Support Agent using Strands Agent framework."""

from pathlib import Path
from typing import Optional

from strands import Agent
from strands_tools import calculator, http_request
from knowledge.wiki_source import WikiKnowledgeSource
from prompts import SUPPORT_AGENT_SYSTEM_PROMPT, MODEL_CONFIG
from tools import SupportAgentTools


class SupportAgent(Agent):
    """AWS Customer Support Agent.
    
    Strands Agent that orchestrates conversation flow and owns all search/retrieve logic.
    Uses WikiKnowledgeSource for file I/O operations only.
    Implements search strategies and aggregates results from knowledge sources.
    """
    
    def __init__(
        self,
        wiki_repo_url: str = "https://github.com/aws-samples/sample-one-click-generative-ai-solutions.wiki.git",
        wiki_local_path: str = "./wiki_data",
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Initialize SupportAgent.
        
        Args:
            wiki_repo_url: GitHub wiki repository URL
            wiki_local_path: Local path to store wiki data
            system_prompt: Custom system prompt for the agent
            **kwargs: Additional arguments passed to Agent constructor
        """
        # Initialize knowledge source (I/O only)
        self.wiki_source = WikiKnowledgeSource(wiki_repo_url, Path(wiki_local_path))
        
        # Initialize tools (contains search/retrieve logic)
        self.support_tools = SupportAgentTools(self.wiki_source)
        
        # Use default system prompt if none provided
        if system_prompt is None:
            system_prompt = SUPPORT_AGENT_SYSTEM_PROMPT
        
        # Initialize Strands Agent with tools
        super().__init__(
            model=MODEL_CONFIG["model_id"],
            system_prompt=system_prompt,
            tools=[
                self.support_tools.search_wiki,
                self.support_tools.list_wiki_files,
                calculator,
                http_request
            ],
            name="AWS Support Agent",
            **kwargs
        )
    
    def search_knowledge(self, query: str) -> str:
        """Search knowledge sources for relevant information.

        Centralizes search logic across all knowledge sources.
        Currently searches wiki, future: AgentCore Memory, Google Drive, etc.

        Args:
            query: Search query

        Returns:
            Aggregated search results
        """
        # Delegate to tools which contain the actual search logic
        return self.support_tools.search_wiki(query)

    async def stream_async(self, user_message: str, **kwargs):
        """Stream agent responses in a format compatible with Genu frontend.

        This method filters the agent's streaming output to only yield messages
        containing an "event" key, which is required by the Genu frontend.

        Args:
            user_message: User's input message
            **kwargs: Additional arguments for the agent

        Yields:
            Messages containing "event" key for frontend consumption
        """
        # Stream messages from the base Agent class
        async for message in super().stream_async(user_message, **kwargs):
            # Only yield messages with "event" key for frontend compatibility
            if "event" in message:
                yield message
