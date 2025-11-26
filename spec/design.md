# Design Document: AWS Customer Support Agent

## Overview

This document outlines the architecture for an AWS customer support agent that serves as an alternative to traditional account managers. The design leverages **Strands Agent** for agent orchestration and **AgentCore** services for runtime, memory, and infrastructure concerns.

## Design Principles

1. **Delegate to Frameworks**: Use Strands Agent's built-in capabilities rather than building custom implementations
2. **Leverage AgentCore Services**: Utilize AgentCore Runtime, Memory, and Identity for infrastructure
3. **Separation of Concerns**: Clear boundaries between agent logic, knowledge sources, and infrastructure
4. **Minimal Complexity**: Simple, cost-effective AWS architecture
5. **Phased Implementation**: Focus on Phase 1 (basic Q&A with repository documents)

---

## 1. Class Architecture

### 1.1 High-Level Class Diagram

```mermaid
classDiagram
    class SupportAgent {
        +model: str
        +session_manager: AgentCoreMemorySessionManager
        +system_prompt: str
        +tools: List[Tool]
        +wiki_source: WikiKnowledgeSource
        +__call__(user_input: str) AgentResponse
        +search_knowledge(query: str) str
    }
    
    class WikiKnowledgeSource {
        +repo_url: str
        +local_path: Path
        +clone_or_update() void
        +load_file(path: Path) str
        +list_files() List[Path]
    }
    
    class AgentCoreMemorySessionManager {
        <<external>>
        +memory_id: str
        +region_name: str
        +add_turns() Event
        +search_long_term_memories() List[MemoryRecord]
        +process_turn_with_llm() Tuple
    }
    
    class BedrockConverseAPI {
        <<external>>
        +invoke_model() Response
    }
    
    SupportAgent --> AgentCoreMemorySessionManager : uses
    SupportAgent --> BedrockConverseAPI : calls via Strands
    SupportAgent --> WikiKnowledgeSource : loads files
    
    note for SupportAgent "Handles search/retrieve logic\nfor all knowledge sources"
    note for WikiKnowledgeSource "Provides file I/O only\nNo search logic"
```

### 1.2 Component Responsibilities

**SupportAgent** (Strands Agent)
- Orchestrates conversation flow using Strands Agent framework
- **Owns all search and retrieve logic** for knowledge sources
- Decides which knowledge sources to query (Wiki, AgentCore Memory, future: Google Drive)
- Implements search strategies (keyword matching, semantic search, etc.)
- Aggregates and ranks results from multiple sources
- Manages tools via `@tool` decorator (no custom tool execution)
- Delegates memory operations to AgentCore Memory
- Uses Bedrock Converse API via Strands model providers

**WikiKnowledgeSource**
- **File I/O operations only** - no search logic
- Clones/updates repository using GitPython
- Loads file contents by path
- Lists available files
- Simple data access layer

**AgentCoreMemorySessionManager** (External)
- Manages short-term memory (conversation history)
- Handles long-term memory extraction (customer facts)
- Provides semantic search capabilities
- Fully managed by AgentCore

**Design Rationale**: Centralizing search/retrieve in SupportAgent enables unified handling of multiple knowledge sources (Wiki, past conversations, Google Drive, etc.) without duplicating search logic. Knowledge sources become simple data providers.

---

## 2. AWS Infrastructure Architecture

### 2.1 Infrastructure Diagram

```mermaid
graph TB
    subgraph "External Application"
        UI[Chat UI<br/>External Integration]
    end
    
    subgraph "AgentCore Runtime"
        Runtime[AgentCore Runtime<br/>Container Orchestration]
        Agent[Support Agent<br/>Strands Agent]
    end
    
    subgraph "AgentCore Services"
        Memory[AgentCore Memory<br/>STM + LTM Strategies]
        Identity[AgentCore Identity<br/>Future: OAuth]
    end
    
    subgraph "AWS Services"
        Bedrock[Amazon Bedrock<br/>Converse API]
        CloudWatch[CloudWatch<br/>Logs + X-Ray Traces]
        ECR[ECR<br/>Container Registry]
    end
    
    subgraph "Knowledge Sources"
        Repo[Repository Documents<br/>Markdown Files]
        Future[Future: Google Drive<br/>Customer Docs]
    end
    
    UI -->|HTTP/WebSocket| Runtime
    Runtime --> Agent
    Agent -->|Store/Retrieve| Memory
    Agent -->|LLM Calls| Bedrock
    Agent -->|Read Files| Repo
    Runtime -->|Traces| CloudWatch
    Runtime -->|Pull Image| ECR
    Agent -.->|Phase 2| Identity
    Agent -.->|Phase 2| Future
```

**Note**: This repository provides the agent implementation only. The chat UI is provided by external applications that integrate with this agent via AgentCore Runtime.

### 2.2 Infrastructure Components

**AgentCore Runtime**
- Serverless container orchestration
- Auto-scaling based on demand
- Built-in X-Ray tracing
- Managed by CloudFormation

**AgentCore Memory**
- Single shared Memory resource for entire IT department
- Session ID: Per-conversation identifier (auto-generated UUID)
- Short-term memory: Conversation history per session (automatic)
- Long-term memory: Semantic extraction with dual-namespace strategy
  - **Per-User Namespaces** (isolated by `{actorId}`):
    - `support/facts/{actorId}` - User-specific AWS resources, issues
    - `support/preferences/{actorId}` - User skill level, settings
  - **Shared Company Namespaces** (accessible to all users):
    - `company/aws-environment` - Shared AWS account structure, VPCs, common resources
    - `company/policies` - Security policies, compliance requirements, best practices
- Retrieval: Semantic search from both user-specific and shared namespaces with relevance scoring

**Amazon Bedrock**
- Model: Claude Sonnet 4 (via Strands model provider)
- API: Converse API with prompt caching
- Prompt cache: Wiki file contents (first prompt)

**CloudWatch + X-Ray**
- Automatic instrumentation via AgentCore
- Transaction Search for GenAI observability
- Log aggregation for debugging

**Repository Documents**
- Source: `https://github.com/icoxfog417/personal-account-manager`
- Access: GitPython clone (no authentication needed for public repository)
- Update: Periodic pull or on-demand

### 2.3 Cost Optimization

- **AgentCore Runtime**: Pay-per-request, no idle costs
- **AgentCore Memory**: Storage + extraction costs only
- **Bedrock**: Prompt caching reduces token costs significantly
- **No Vector DB**: File-based search in Phase 1 (minimal cost)
- **No NAT Gateway**: AgentCore handles networking

---

## 3. Directory Structure

```
personal-account-manager/
├── spec/
│   ├── requirements.md          # Project requirements
│   └── design.md                # This document
│
├── agent/
│   ├── __init__.py
│   ├── __main__.py           # AgentCore entrypoint
│   ├── support_agent.py      # SupportAgent class (Strands Agent)
│   ├── prompts.py            # Prompt and model settings
│   ├── tools.py              # Tool definitions (@tool decorator)
│   ├── requirements.txt      # Agent dependencies
│   ├── Dockerfile            # Container configuration
│   └── knowledge/
│       ├── __init__.py
│       └── wiki_source.py    # WikiKnowledgeSource class
│
├── cdk/
│   ├── app.py                # CDK app entry point
│   ├── support_agent_stack.py # Stack definition
│   ├── cdk.json              # CDK configuration
│   └── requirements.txt      # CDK dependencies
│
├── tests/
│   ├── unit/
│   │   ├── test_agent.py
│   │   └── test_wiki_source.py
│   └── integration/
│       └── test_e2e.py
│
└── README.md                    # Project documentation
```

### 3.1 Key Files

**agent/support_agent.py**
- SupportAgent class (Strands Agent)
- Implements search/retrieve logic for all knowledge sources

**agent/tools.py**
- Tool definitions using `@tool` decorator
- Search and retrieval functions

**agent/knowledge/wiki_source.py**
- WikiKnowledgeSource class
- Provides file I/O operations only (clone, load, list)

**agent/__main__.py**
- AgentCore entrypoint with `@app.entrypoint` decorator
- Integrates SupportAgent with BedrockAgentCoreApp

**cdk/support_agent_stack.py**
- CDK stack for deploying agent to AgentCore Runtime
- Docker image asset and runtime configuration

---

## 4. Data Flow

### 4.1 Conversation Flow

```mermaid
sequenceDiagram
    participant User
    participant ExternalApp
    participant SupportAgent
    participant WikiSource
    participant AgentCoreMemory
    participant BedrockAPI
    
    User->>ExternalApp: Enter question
    ExternalApp->>SupportAgent: Process input
    
    SupportAgent->>AgentCoreMemory: Retrieve relevant facts
    AgentCoreMemory-->>SupportAgent: Customer context
    
    SupportAgent->>WikiSource: Load files (via tool)
    WikiSource-->>SupportAgent: File contents
    
    SupportAgent->>BedrockAPI: Generate response (with context)
    BedrockAPI-->>SupportAgent: LLM response
    
    SupportAgent->>AgentCoreMemory: Store conversation turn
    AgentCoreMemory-->>SupportAgent: Event stored
    
    SupportAgent-->>ExternalApp: Response
    ExternalApp-->>User: Display answer
    
    Note over AgentCoreMemory: Background: Extract facts to LTM
```

## 5. Deployment Strategy

### 5.1 Simplified CDK Deployment Architecture

**Deployment Approach**
- Use AWS CDK (Python) for infrastructure as code
- Leverage CDK Docker image assets for automatic build and push
- Auto-created IAM roles via AgentCore
- Single command deployment: `cdk deploy`

**Key Simplifications**
- No custom Lambda trigger needed - CDK handles Docker build automatically
- No custom IAM role construct - AgentCore auto-creates roles
- Minimal infrastructure code - focus on agent deployment

**CDK Stack Components**

```mermaid
graph TB
    subgraph "CDK Stack"
        Stack[SupportAgentStack]
        
        subgraph "Container Management"
            DockerAsset[Docker Image Asset]
            ECR[ECR Repository]
        end
        
        subgraph "AgentCore Resources"
            Runtime[AgentCore Runtime]
        end
        
        subgraph "Observability"
            Logs[CloudWatch Logs]
            XRay[X-Ray Tracing]
        end
    end
    
    Stack --> DockerAsset
    DockerAsset --> ECR
    Stack --> Runtime
    ECR --> Runtime
    Runtime --> Logs
    Runtime --> XRay
```

### 5.2 Simplified CDK Stack Structure

**Directory Layout**
```
cdk/
├── app.py                          # CDK app entry point
├── support_agent_stack.py          # Main stack definition
├── cdk.json                        # CDK configuration
└── requirements.txt                # CDK dependencies (aws-cdk-lib only)
```

**Stack Resources**

1. **Docker Image Asset**
   - CDK automatically builds Docker image from `../agent` directory
   - Pushes to auto-created ECR repository
   - Handles ARM64 architecture
   - No CodeBuild or Lambda needed

2. **AgentCore Runtime**
   - References Docker image asset URI
   - Network mode: PUBLIC (configurable)
   - Protocol: HTTP
   - Auto-creates execution role with required permissions
   - Environment variables for AWS region

**Stack Parameters**
- `AgentName`: Name for the agent runtime (default: "SupportAgent")
- `NetworkMode`: PUBLIC or PRIVATE (default: "PUBLIC")

**Stack Outputs**
- `AgentRuntimeId`: Runtime resource ID
- `AgentRuntimeArn`: Runtime ARN for invocation
- `ImageUri`: Docker image URI in ECR

### 5.3 Simplified Deployment Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant CDK as CDK CLI
    participant Docker as Docker Build
    participant ECR
    participant CFN as CloudFormation
    participant AgentCore as AgentCore Runtime
    
    Dev->>CDK: cdk deploy
    CDK->>Docker: Build image from agent/
    Docker->>ECR: Push image (auto-created repo)
    CDK->>CFN: Create stack
    CFN->>AgentCore: Create runtime (auto-create role)
    AgentCore->>ECR: Pull image
    AgentCore-->>CFN: Runtime ready
    CFN-->>CDK: Stack complete
    CDK-->>Dev: Outputs (ARN, URI)
```

**Deployment Steps**
1. Developer runs `cdk deploy`
2. CDK builds Docker image locally (or in cloud if configured)
3. CDK pushes image to auto-created ECR repository
4. CloudFormation creates AgentCore Runtime
5. AgentCore auto-creates execution role with required permissions
6. Runtime pulls image from ECR
7. Stack outputs runtime ARN

**Deployment Time**: 5-8 minutes
- Docker build and push: ~3-5 minutes
- Runtime provisioning: ~2-3 minutes

### 5.4 Docker Container Configuration

**Dockerfile Location**: `agent/Dockerfile`

```dockerfile
FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir aws-opentelemetry-distro==0.10.1

# Environment variables
ENV AWS_REGION=us-west-2
ENV AWS_DEFAULT_REGION=us-west-2

# Non-root user for security
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

# Expose ports
EXPOSE 8080 8000

# Copy agent code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/ping || exit 1

# Start with OpenTelemetry instrumentation
CMD ["opentelemetry-instrument", "python", "-m", "agent"]
```

**Key Features**
- Python 3.11 slim base image
- OpenTelemetry auto-instrumentation
- Non-root user for security
- Health check endpoint
- Ports 8080 (HTTP) and 8000 (metrics)

### 5.5 Agent Entrypoint Integration

**agent/__main__.py** (already exists)
```python
from bedrock_agentcore import BedrockAgentCoreApp
from agent.support_agent import SupportAgent

app = BedrockAgentCoreApp()

@app.entrypoint
async def entrypoint(payload):
    agent = SupportAgent(
        repo_url="https://github.com/icoxfog417/personal-account-manager",
        knowledge_dir="docs",
        local_path="./repo_data"
    )
    
    message = payload.get("prompt", "")
    async for msg in agent.stream_async(message):
        if "event" in msg:
            yield msg

if __name__ == "__main__":
    app.run()
```

**Integration Points**
- `BedrockAgentCoreApp`: AgentCore runtime integration
- `@app.entrypoint`: Decorator for runtime invocation
- Streaming responses via async generator
- Payload format: `{"prompt": "user message"}`

### 5.6 CDK Deployment Commands

**Initial Setup**
```bash
cd cdk
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Bootstrap (First Time)**
```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

**Deploy**
```bash
cdk deploy
```

**View Outputs**
```bash
cdk deploy --outputs-file outputs.json
```

**Destroy**
```bash
cdk destroy
```

**Synthesize Template**
```bash
cdk synth > template.yaml
```

### 5.7 Testing Deployed Agent

**Using AWS CLI**
```bash
# Get runtime ARN from outputs
RUNTIME_ARN=$(aws cloudformation describe-stacks \
  --stack-name SupportAgentStack \
  --query 'Stacks[0].Outputs[?OutputKey==`AgentRuntimeArn`].OutputValue' \
  --output text)

# Invoke agent
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn $RUNTIME_ARN \
  --qualifier DEFAULT \
  --payload $(echo '{"prompt": "What is AWS Lambda?"}' | base64) \
  response.json

# View response
cat response.json
```

**Using AWS Console**
1. Navigate to Bedrock AgentCore Console
2. Go to "Runtimes"
3. Find "SupportAgentStack_SupportAgent"
4. Click "Test"
5. Enter payload: `{"prompt": "Your question"}`
6. View streaming response

### 5.8 IAM Permissions

**Auto-Created Roles**
- AgentCore automatically creates execution role with required permissions:
  - ECR image pull
  - CloudWatch Logs write
  - X-Ray tracing
  - Bedrock model invocation
  - AgentCore workload identity

**Developer Permissions Required**
- `BedrockAgentCoreFullAccess` managed policy
- `AmazonBedrockFullAccess` managed policy (or scoped Bedrock permissions)
- IAM permissions to create roles (for auto-creation)
- ECR repository management
- CloudFormation stack operations

---

## 6. Phase 1 Implementation Focus

### 6.1 In Scope

✅ Agent implementation (no chat UI in this repository)
✅ Repository document integration (clone + file search)
✅ Conversation memory (STM + LTM via AgentCore)
✅ Basic Q&A with context retrieval
✅ Strands Agent with `@tool` decorator
✅ AgentCore Memory with semantic strategy
✅ Bedrock Converse API with prompt caching
✅ CDK deployment with Docker image assets

### 6.2 Out of Scope (Phase 2)

❌ Chat UI (provided by external applications)
❌ Email interface
❌ Command execution (billing alerts, credit application)
❌ External knowledge sources (Google Drive)
❌ AgentCore Identity integration
❌ Advanced personalization
❌ Multi-agent orchestration

---

## 7. Key Design Decisions

### 7.1 Why Strands Agent?

- **Built-in tool management**: `@tool` decorator handles tool execution
- **Session management**: Integrates with AgentCore Memory seamlessly
- **Model flexibility**: Easy to swap LLM providers
- **Streaming support**: Ready for real-time responses

### 7.2 Why AgentCore Memory?

- **Managed service**: No infrastructure to maintain
- **Automatic extraction**: LTM strategies run in background
- **Semantic search**: Built-in vector search capabilities
- **Scalable**: Handles multiple users/sessions

### 7.3 Why File-Based Document Search (Phase 1)?

- **Simplicity**: No vector DB setup/cost
- **Sufficient for MVP**: Documentation is small, keyword search works
- **Fast iteration**: Focus on agent logic, not infrastructure
- **Upgrade path**: Can add vector search in Phase 2

### 7.4 Why No Custom Tool Execution?

- **Strands handles it**: `@tool` decorator provides all needed functionality
- **Less code**: No need to build tool registry, validation, error handling
- **Better integration**: Works seamlessly with AgentCore Runtime

---

## 8. Success Metrics

### 8.1 Technical Metrics

- Response latency: < 3 seconds (p95)
- Memory retrieval accuracy: > 80% relevant facts
- Document search relevance: > 70% helpful results
- System uptime: > 99.5%

### 8.2 Business Metrics

- Customer satisfaction: > 4/5 rating
- Issue resolution rate: > 60% without escalation
- Cost per interaction: < $0.10
- Adoption rate: > 50% of target customers

---

## 9. Future Enhancements (Phase 2+)

### 9.1 Email Interface

- Receive questions via email (SES)
- Parse email content and attachments
- Send formatted responses with links

### 9.2 Command Execution

- Billing alert setup (CloudWatch alarms)
- Credit application workflow (Step Functions)
- Payment method changes (AWS Billing API)
- Approval workflows for sensitive operations

### 9.3 Enhanced Knowledge Sources

- Google Drive integration (AgentCore Identity)
- Customer-specific documentation
- Real-time AWS service status
- Internal knowledge bases

### 9.4 Advanced Personalization

- Learning from interaction patterns
- Proactive suggestions based on usage
- Custom response styles per customer
- Multi-language support

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Document content quality | High | Curate documentation, add validation |
| LLM hallucinations | High | Prompt engineering, fact-checking |
| Memory extraction accuracy | Medium | Tune strategies, monitor quality |
| Cost overruns | Medium | Set budgets, monitor usage |
| Slow response times | Medium | Optimize prompts, use caching |
| Security concerns | High | Use AgentCore Identity, audit logs |

---

## Conclusion

This design leverages Strands Agent and AgentCore services to build a scalable, cost-effective AWS customer support agent. By delegating infrastructure concerns to managed services and focusing on agent logic and knowledge integration, we can rapidly iterate and deliver value to customers who lack dedicated account manager support.

The phased approach ensures we validate core functionality (Phase 1) before adding complexity (Phase 2), while the architecture remains flexible enough to accommodate future enhancements.
