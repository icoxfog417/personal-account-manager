# Support Agent CDK - TypeScript

TypeScript CDK deployment for AWS Customer Support Agent using AgentCore Runtime.

## Prerequisites

- Node.js 18+ and npm
- AWS CLI configured
- AWS CDK CLI: `npm install -g aws-cdk`
- CDK version 2.220.0 or later (for BedrockAgentCore support)

## Setup

```bash
# Install dependencies
npm install

# Bootstrap CDK (first time only)
cdk bootstrap

# Build TypeScript
npm run build
```

## Deployment

```bash
# Deploy the stack
cdk deploy

# Deploy with parameters
cdk deploy --parameters AgentName=MyAgent --parameters NetworkMode=PUBLIC
```

## Configuration

Edit `cdk.json` to configure agent settings:

```json
{
  "context": {
    "agent_config": {
      "repo_url": "https://github.com/icoxfog417/personal-account-manager",
      "knowledge_dir": "docs",
      "local_path": "./repo_data",
      "system_prompt": ""
    }
  }
}
```

## Architecture

- **ECR Repository**: Stores Docker image
- **CodeBuild**: Builds ARM64 Docker image
- **Lambda**: Triggers CodeBuild during deployment
- **AgentCore Runtime**: Hosts the agent container
- **IAM Roles**: Execution permissions

## Testing

```bash
# Get runtime ARN
RUNTIME_ARN=$(aws cloudformation describe-stacks \
  --stack-name SupportAgentStack \
  --query 'Stacks[0].Outputs[?OutputKey==`AgentRuntimeArn`].OutputValue' \
  --output text)

# Invoke agent
aws bedrock-agentcore invoke-agent-runtime \
  --agent-runtime-arn $RUNTIME_ARN \
  --qualifier DEFAULT \
  --payload $(echo '{"prompt": "Hello"}' | base64) \
  response.json
```

## Cleanup

```bash
cdk destroy
```

## Development

```bash
# Watch mode
npm run watch

# Synthesize CloudFormation
cdk synth

# Compare changes
cdk diff
```
