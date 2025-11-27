#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SupportAgentStack } from '../lib/support-agent-stack';

const app = new cdk.App();
new SupportAgentStack(app, 'SupportAgentStack');
