# AWS Customer Support Agent

An AI-powered customer support agent that serves as an alternative to traditional account managers, built with Strands Agent and deployed on AgentCore Runtime.

## Features

- **Knowledge Integration**: Searches AWS documentation from GitHub wiki
- **Conversation Memory**: Stores customer context using AgentCore Memory
- **Serverless Deployment**: Runs on AgentCore Runtime with auto-scaling
- **One-Click Deployment**: CloudFormation template for easy setup

## Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.11+ with `uv` package manager
- Docker (for local development)

### One-Click Deployment

[![Launch Stack](https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png)](https://console.aws.amazon.com/cloudformation/home#/stacks/new?stackName=aws-support-agent&templateURL=https://raw.githubusercontent.com/aws-samples/personal-account-manager/main/infrastructure/cloudformation/deployment-stack.yaml)

Or deploy via CLI:

```bash
./infrastructure/scripts/deploy.sh your-email@example.com
```

### Local Development

1. **Setup Environment**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

2. **Run Tests**:
   ```bash
   uv run pytest tests/
   uv run ruff check
   ```

3. **Local Testing**:
   ```bash
   uv run python -c "
   from src.agent.support_agent import SupportAgent
   from src.knowledge.wiki_source import WikiKnowledgeSource
   from src.config.settings import Settings
   
   wiki = WikiKnowledgeSource(Settings.WIKI_REPO_URL, Settings.WIKI_LOCAL_PATH)
   agent = SupportAgent(Settings.MODEL_NAME, wiki, Settings.SYSTEM_PROMPT)
   print(agent.search_wiki_files('lambda'))
   "
   ```

## Architecture

- **SupportAgent**: Strands Agent with search/retrieve logic for all knowledge sources
- **WikiKnowledgeSource**: File I/O operations for GitHub wiki repository
- **AgentCore Memory**: Conversation history and customer fact extraction
- **Amazon Bedrock**: Claude Sonnet 4 via Converse API with prompt caching

## Project Structure

```
├── src/
│   ├── agent/          # Strands Agent implementation
│   ├── knowledge/      # Knowledge source classes
│   └── config/         # Configuration management
├── infrastructure/     # CloudFormation and deployment scripts
├── tests/             # Unit and integration tests
└── data/              # Local wiki repository
```

## Configuration

Key settings in `src/config/settings.py`:

- `WIKI_REPO_URL`: GitHub wiki repository
- `MODEL_NAME`: Bedrock model identifier
- `MEMORY_ID`: AgentCore Memory resource ID
- `SYSTEM_PROMPT`: Agent behavior instructions

## Development Guidelines

Follow the coding standards in `.amazonq/rules/project.md`:

- Use `uv run` for all Python operations
- Type hints required for all functions
- Use f-strings for string formatting
- Test with `pytest`, format with `ruff`

## Deployment

### AgentCore Deployment

Deploy the agent to AWS Bedrock AgentCore Runtime:

1. **Configure Agent**:
   ```bash
   cd agent
   agentcore configure --entrypoint support_agent.py
   ```

2. **Deploy**:
   ```bash
   agentcore launch
   ```
   This will:
   - Build ARM64 container in CodeBuild
   - Push to ECR
   - Deploy to AgentCore Runtime
   - Configure observability

3. **Test**:
   ```bash
   agentcore invoke '{"prompt": "Amazon Bedrockとは何ですか？"}'
   ```

4. **Monitor Logs**:
   ```bash
   aws logs tail /aws/bedrock-agentcore/runtimes/<agent-arn> --follow
   ```

### Important Notes

- **Documentation Files**: Knowledge base files must use `.txt` extension (not `.md`) to bypass AgentCore's dockerignore filtering
- **Data Directory**: Place documentation in `agent/data/*.txt`
- **Memory**: AgentCore Memory is automatically configured for conversation history

### CloudFormation Deployment (Alternative)

The CloudFormation stack creates:

- AgentCore Runtime for container orchestration
- AgentCore Memory with semantic strategies
- ECR repository for container images
- CodeBuild project for automated deployment
- SNS notifications for deployment status

## Cost Optimization

- **Pay-per-request**: No idle costs with AgentCore Runtime
- **Prompt caching**: Reduces Bedrock token costs
- **File-based search**: No vector database costs in Phase 1
- **Managed services**: Minimal infrastructure overhead

## Support

For issues or questions:

1. Check the [GitHub Issues](https://github.com/aws-samples/personal-account-manager/issues)
2. Review the [Design Document](spec/design.md)
3. Contact the development team

## License

This project is licensed under the MIT-0 License. See the LICENSE file for details.
