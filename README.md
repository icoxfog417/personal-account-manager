# AWS Customer Support Agent

An AI-powered customer support agent that serves as an alternative to traditional account managers, built with Strands Agent and deployed on AgentCore Runtime.

## Features

- **Knowledge Integration**: Searches repository documentation from GitHub
- **Conversation Memory**: Stores customer context using AgentCore Memory (STM + LTM)
- **Serverless Deployment**: Runs on AgentCore Runtime with auto-scaling
- **CDK Deployment**: Infrastructure as code with AWS CDK

## Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.11+ with `uv` package manager
- Docker (for container builds)
- Node.js 18+ (for CDK)

### Deploy with CDK

1. **Bootstrap CDK** (first time only):
   ```bash
   cd cdk
   cdk bootstrap aws://ACCOUNT-ID/REGION
   ```

2. **Deploy Stack**:
   ```bash
   cdk deploy
   ```

3. **Get Runtime ARN**:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name SupportAgentStack \
     --query 'Stacks[0].Outputs[?OutputKey==`AgentRuntimeArn`].OutputValue' \
     --output text
   ```

### Local Development

1. **Setup Environment**:
   ```bash
   uv venv
   source .venv/bin/activate
   cd agent
   uv pip install -r requirements.txt
   ```

2. **Run Tests**:
   ```bash
   uv run pytest tests/
   uv run ruff check
   ```

## Architecture

- **SupportAgent**: Strands Agent with search/retrieve logic for all knowledge sources
- **WikiKnowledgeSource**: File I/O operations for GitHub repository
- **AgentCore Memory**: Conversation history (STM) and customer fact extraction (LTM)
- **Amazon Bedrock**: Claude Sonnet 4 via Converse API with prompt caching
- **AgentCore Runtime**: Serverless container orchestration with auto-scaling

## Project Structure

```
├── agent/              # Agent implementation
│   ├── __main__.py    # AgentCore entrypoint
│   ├── support_agent.py
│   ├── tools.py
│   ├── prompts.py
│   ├── knowledge/     # Knowledge source classes
│   └── Dockerfile
├── cdk/               # CDK infrastructure
│   ├── app.py
│   └── support_agent_stack.py
├── tests/             # Unit and integration tests
└── spec/              # Design documentation
```

## Configuration

Key environment variables:

- `AWS_REGION`: AWS region for Bedrock and AgentCore
- `MEMORY_ID`: AgentCore Memory resource ID (optional)
- Repository URL and paths configured in agent code

## Development Guidelines

Follow the coding standards in `.kiro/steering/`:

- Use `uv run` for all Python operations
- Type hints required for all functions
- Use f-strings for string formatting
- Test with `pytest`, format with `ruff`
- Follow test-first interface design workflow

## Deployment

### CDK Deployment

1. **Install Dependencies**:
   ```bash
   cd cdk
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Deploy Stack**:
   ```bash
   cdk deploy
   ```
   
   This automatically:
   - Builds Docker image from `agent/` directory
   - Pushes to auto-created ECR repository
   - Creates AgentCore Runtime with execution role
   - Configures CloudWatch Logs and X-Ray tracing

3. **Test Deployed Agent**:
   ```bash
   RUNTIME_ARN=$(aws cloudformation describe-stacks \
     --stack-name SupportAgentStack \
     --query 'Stacks[0].Outputs[?OutputKey==`AgentRuntimeArn`].OutputValue' \
     --output text)
   
   aws bedrock-agentcore invoke-agent-runtime \
     --agent-runtime-arn $RUNTIME_ARN \
     --qualifier DEFAULT \
     --payload $(echo '{"prompt": "What is AWS Lambda?"}' | base64) \
     response.json
   ```

4. **View Logs**:
   ```bash
   aws logs tail /aws/bedrock-agentcore/runtimes/$RUNTIME_ARN --follow
   ```

### Deployment Time

- Docker build and push: ~3-5 minutes
- Runtime provisioning: ~2-3 minutes
- Total: ~5-8 minutes

### Required IAM Permissions

- `BedrockAgentCoreFullAccess` managed policy
- `AmazonBedrockFullAccess` managed policy
- IAM role creation permissions
- ECR repository management
- CloudFormation stack operations

## Cost Optimization

- **Pay-per-request**: No idle costs with AgentCore Runtime
- **Prompt caching**: Reduces Bedrock token costs
- **File-based search**: No vector database costs in Phase 1
- **Auto-scaling**: Resources scale with demand
- **Managed services**: Minimal infrastructure overhead

## GenU Integration

This agent is designed to integrate with [GenU](https://github.com/aws-samples/generative-ai-use-cases) through the [one-click deployment process](https://github.com/aws-samples/sample-one-click-generative-ai-solutions).

The CDK stack is automatically tagged with `Integration:GenU`, which enables:
- **Automatic Discovery**: The one-click deployment process discovers this stack by the tag
- **Agent Registration**: The deployed agent is automatically registered as an available agent in GenU
- **Seamless Integration**: No manual configuration needed for GenU integration

To deploy with GenU integration, simply deploy this stack using CDK and the one-click deployment process will automatically detect and register it.

## Phase 1 Scope

This implementation focuses on:

✅ Repository document integration (clone + file search)  
✅ Conversation memory (STM + LTM via AgentCore)  
✅ Basic Q&A with context retrieval  
✅ Strands Agent with `@tool` decorator  
✅ CDK deployment with Docker image assets  

Phase 2 will add email interface, command execution, and external knowledge sources.

## Support

For issues or questions:

1. Check the [GitHub Issues](https://github.com/icoxfog417/personal-account-manager/issues)
2. Review the [Design Document](spec/design.md)
3. Review the [Requirements Document](spec/requirements.md)

## License

This project is licensed under the MIT-0 License.
