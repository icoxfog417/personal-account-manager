import * as cdk from 'aws-cdk-lib';
import * as agentcore from '@aws-cdk/aws-bedrock-agentcore-alpha';
import * as path from 'path';
import { Construct } from 'constructs';

export class SupportAgentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    cdk.Tags.of(this).add('Integration', 'GenU');

    const agentConfig = this.node.tryGetContext('agent_config') || {};

    const agentName = new cdk.CfnParameter(this, 'AgentName', {
      type: 'String',
      default: 'SupportAgent',
      description: 'Name for the agent runtime',
    });

    const agentRuntimeArtifact = agentcore.AgentRuntimeArtifact.fromAsset(
      path.join(__dirname, '../../agent')
    );

    const envVars: { [key: string]: string } = {
      AWS_DEFAULT_REGION: this.region,
      AGENT_REPO_URL: agentConfig.repo_url || '',
      AGENT_KNOWLEDGE_DIR: agentConfig.knowledge_dir || 'docs',
      AGENT_LOCAL_PATH: agentConfig.local_path || './repo_data',
    };

    if (agentConfig.system_prompt) {
      envVars.AGENT_SYSTEM_PROMPT = agentConfig.system_prompt;
    }

    const runtime = new agentcore.Runtime(this, 'AgentRuntime', {
      runtimeName: `${this.stackName.replace(/-/g, '_')}_${agentName.valueAsString}`,
      agentRuntimeArtifact,
      networkConfiguration: agentcore.RuntimeNetworkConfiguration.usingPublicNetwork(),
      description: `Support agent runtime for ${this.stackName}`,
      environmentVariables: envVars,
    });

    runtime.role!.addToPrincipalPolicy(
      new cdk.aws_iam.PolicyStatement({
        effect: cdk.aws_iam.Effect.ALLOW,
        actions: ['bedrock:InvokeModel', 'bedrock:InvokeModelWithResponseStream'],
        resources: [
          'arn:aws:bedrock:*::foundation-model/*',
          `arn:aws:bedrock:${this.region}:${this.account}:inference-profile/*`,
        ],
      })
    );

    new cdk.CfnOutput(this, 'AgentCoreRuntimeName', {
      description: 'Name of the created agent runtime',
      value: 'Personal AWS Support Agent',
    });

    new cdk.CfnOutput(this, 'AgentCoreRuntimeId', {
      description: 'ID of the created agent runtime',
      value: runtime.agentRuntimeId,
    });

    new cdk.CfnOutput(this, 'AgentCoreRuntimeArn', {
      description: 'ARN of the created agent runtime',
      value: runtime.agentRuntimeArn,
    });

    new cdk.CfnOutput(this, 'AgentRoleArn', {
      description: 'ARN of the agent execution role',
      value: runtime.role!.roleArn,
    });
  }
}
