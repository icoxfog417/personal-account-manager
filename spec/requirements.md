# Project Requirements: AWS Customer Support Agent

## Project Purpose

Build an AWS customer support agent that serves as an alternative to traditional account managers. By leveraging generative AI agent technology, we aim to provide support to thousands of AWS customers who currently lack dedicated account manager assistance, reducing opportunity loss and customer dissatisfaction.

## Objectives

* Remove any obstacles for every customer
* Provide not only efficient but also exciting onboarding experiences

## Current Problems

* Not every customer receives support from an account manager
* Cost and security-related issues cause dissatisfaction
* Account managers spend time on repetitive tasks (explaining credit applications, payment method changes, etc.)
* These repetitive tasks prevent both customers and account managers from focusing on building AWS experiences
* Valuable materials created by account managers are not shared or disclosed across the organization

## Approach

* Integrate all necessary information in repository documentation at `https://github.com/icoxfog417/personal-account-manager`
* Build an AI agent that answers customer questions by referencing documentation files (markdown files, PDFs, YouTube videos, etc.)
* Enable customers to interact with the agent and delegate trustworthy operations (setting billing alerts, applying credits, etc.)
* Store customer-specific issues alongside documentation content to enable personalization

## Implementation

* Leverage Strands Agent to build the agent
* Deploy to AgentCore Runtime using CloudFormation
* Receive questions via email rather than chat UI
* Use AgentCore Memory to store conversations and extract important customer facts

## Customer Experience

**NOTE: We focus on implementing Phase 1, but share future direction for architecture decisions**

### 1. Send Question to Agent
* **Phase 1**: Send message via chat UI
* **Phase 2**: Send message via email

### 2. Knowledge Source Integration
* Clone repository containing documentation files
* **Phase 2**: Integrate customer's original knowledge sources (Google Drive, etc.) by leveraging AgentCore Identity

### 3. Answer Questions
* Use Amazon Bedrock Converse API to inject file contents into prompts
* Store conversation history in AgentCore Memory's short-term memory
* Apply prompt cache for the first prompt (file contents)
* **Phase 2**: Propose and execute commands for specific operations (commands prepared in wiki)

### 4. Personalization
* Store important customer information in AgentCore Memory's long-term memory:
  * Customer environment details
  * Skill level
  * Applied settings
