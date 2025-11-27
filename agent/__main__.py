# agent/__main__.py
import os
from bedrock_agentcore import BedrockAgentCoreApp
from agent.support_agent import SupportAgent

app = BedrockAgentCoreApp()

@app.entrypoint
async def entrypoint(payload):
    # Read configuration from environment variables
    repo_url = os.getenv("AGENT_REPO_URL", "https://github.com/icoxfog417/personal-account-manager")
    knowledge_dir = os.getenv("AGENT_KNOWLEDGE_DIR", "docs")
    local_path = os.getenv("AGENT_LOCAL_PATH", "./repo_data")
    system_prompt = os.getenv("AGENT_SYSTEM_PROMPT")
    
    # Initialize SupportAgent with configuration
    agent_kwargs = {
        "repo_url": repo_url,
        "knowledge_dir": knowledge_dir,
        "local_path": local_path,
    }
    if system_prompt:
        agent_kwargs["system_prompt"] = system_prompt
    
    agent = SupportAgent(**agent_kwargs)
    
    message = payload.get("prompt", "")
    async for msg in agent.stream_async(message):
        if "event" in msg:
            yield msg

if __name__ == "__main__":
    app.run()
