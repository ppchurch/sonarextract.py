#SonarCloud Issue Extractor
This Python script fetches issues from a SonarCloud project and formats them into detailed markdown code blocks, optimized for passing to Large Language Models (LLMs) for automated or guided code fixes. It extracts rich metadata (e.g., issue key, rule ID, effort, code context) and provides tailored fix prompts, making it ideal for improving code quality in large codebases, especially those with React/TypeScript components.
Features

Fetches SonarCloud Issues: Queries the SonarCloud API to retrieve open issues for a specified project.
Rich Metadata: Includes issue key, rule ID, severity, effort estimate, tags, status, and rule description.
Code Context: Retrieves surrounding code (±5 lines) for better issue context.
LLM-Optimized Output: Formats issues in markdown with tailored fix prompts for common issues (e.g., React accessibility, unused imports).
Pagination Support: Handles large repositories with hundreds of issues.
Customizable: Easily extendable for additional fields or output formats.

##Use Case
Perfect for developers maintaining large projects (e.g., web apps with React/TSX, Node/TS backends) who want to:

Extract SonarCloud issues for manual or LLM-assisted fixes.
Prioritize high-impact issues (e.g., accessibility violations, React key prop issues).
Automate code quality workflows in CI/CD pipelines.

##Prerequisites

Python 3.6+
requests library (pip install requests)
SonarCloud account with an API token
Project key for your SonarCloud repository

##Installation

Clone this repository:git clone https://github.com/your-username/sonarcloud-issue-extractor.git
cd sonarcloud-issue-extractor


Install dependencies:pip install requests



##Configuration

Generate SonarCloud API Token:
Log into SonarCloud, go to My Account > Security, and generate a token.
Copy the token securely (do not commit it to version control).


##Set Project Key:
Find your project key in the SonarCloud dashboard (e.g., your-org_project-name).


##Update Script:
Open extract_sonarcloud_issues.py and replace the placeholders:SONAR_TOKEN = "your_sonarcloud_api_token"
PROJECT_KEY = "your_project_key"





##Usage
Run the script to fetch and format issues:
python extract_sonarcloud_issues.py

The script will:

Query the SonarCloud API for open issues.
Fetch code context and rule details.
Output issues in markdown code blocks to the console.

##Example Output
For a React/TSX project, the output might look like:
Issue Key: AWt9xY2Z3k4m5n6p7q8r
Project: your-org_project-name
Module: SOURCE/your-app
File: apps/frontend/components/Sidebar.tsx
Line: 3
Type: CODE_SMELL
Severity: MINOR
Rule ID: typescript:S1128
Rule Description: Unused imports
Effort to Fix: 2min
Tags: maintainability
Status: OPEN
Issue: Remove this unused import of 'Building'.
Code Context:
1: import React from 'react';
2: import { Building, Settings } from './icons';
3: import { SidebarProps } from './types';
4: const Sidebar = ({ items }: SidebarProps) => {
LLM Fix Prompt: Remove the specified import statement from the file.
Suggested Fix: (Provide a fix for the above issue)

##Using with LLMs
Copy the output and use it in an LLM prompt, e.g.:
Apply the suggested fixes for these SonarCloud issues:
[paste markdown output here]

The LLM Fix Prompt field provides specific guidance (e.g., "Add htmlFor attribute to label in JSX" for accessibility issues).
Customization

Add Fields: Modify fetch_sonarcloud_issues to include more API fields (e.g., creationDate, assignee) via additionalFields.
Change Format: Edit format_issues_for_llm to output JSON or custom markdown.
Extend Prompts: Update generate_fix_prompt to handle more issue types (e.g., add prompts for "CRITICAL" issues like deep function nesting).

##Notes

API Limits: SonarCloud’s API caps at 500 issues per request. The script paginates to handle larger repos.
Code Context: Snippets may fail for private repos or large files. Check SonarCloud permissions if "No context available" appears frequently.
Performance: Rule description queries add API calls. For very large repos (>

