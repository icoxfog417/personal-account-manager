"""SupportAgent - AWS Customer Support Agent using Strands Agent framework."""

from pathlib import Path
from typing import Optional

from strands import Agent
from strands_tools import calculator, http_request
from agent.knowledge.wiki_source import WikiKnowledgeSource
from agent.prompts import SUPPORT_AGENT_SYSTEM_PROMPT, MODEL_CONFIG
from agent.tools import SupportAgentTools


class SupportAgent(Agent):
    """AWS Customer Support Agent.
    
    Strands Agent that orchestrates conversation flow and owns all search/retrieve logic.
    Uses WikiKnowledgeSource for file I/O operations only.
    Implements search strategies and aggregates results from knowledge sources.
    """
    
    def __init__(
        self,
        repo_url: str = "https://github.com/icoxfog417/personal-account-manager",
        knowledge_dir: str = "docs",
        local_path: str = "./repo_data",
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        """Initialize SupportAgent.
        
        Args:
            repo_url: Repository URL containing knowledge files
            knowledge_dir: Directory path within repository containing knowledge files
            local_path: Local path to store repository data
            system_prompt: Custom system prompt for the agent
            **kwargs: Additional arguments passed to Agent constructor
        """
        # Initialize knowledge source (I/O only)
        self.wiki_source = WikiKnowledgeSource(repo_url, knowledge_dir, Path(local_path))
        
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
        Also passes through the final "result" message for invoke_async compatibility.

        Args:
            user_message: User's input message
            **kwargs: Additional arguments for the agent

        Yields:
            Messages containing "event" or "result" key
        """
        # Stream messages from the base Agent class
        async for message in super().stream_async(user_message, **kwargs):
            # Yield messages with "event" key (for frontend) or "result" key (for invoke_async)
            if "event" in message or "result" in message:
                yield message
