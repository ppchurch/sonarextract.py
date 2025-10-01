import requests
import json
import os
from uuid import uuid4

# Configuration - read from environment variables
SONAR_TOKEN = os.environ.get("SONAR_TOKEN")
if not SONAR_TOKEN:
    raise ValueError("SONAR_TOKEN environment variable is required. Set it with: export SONAR_TOKEN='your-token-here'")

PROJECT_KEY = os.environ.get("PROJECT_KEY")
if not PROJECT_KEY:
    raise ValueError("PROJECT_KEY environment variable is required. Set it with: export PROJECT_KEY='your-project-key'")

SONAR_URL = "https://sonarcloud.io/api"

def fetch_sonarcloud_issues():
    # Set up API request
    headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}
    params = {
        "projectKeys": PROJECT_KEY,
        "statuses": "OPEN,CONFIRMED",  # Fetch open issues
        "ps": 100,  # Page size (max 500)
        "p": 1,  # Page number
        "additionalFields": "flows,rules"  # Include flow data and rule details
    }
    issues = []
    
    # Paginate through issues
    while True:
        response = requests.get(f"{SONAR_URL}/issues/search", headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error fetching issues: {response.status_code} - {response.text}")
            break
        
        data = response.json()
        issues.extend(data.get("issues", []))
        
        # Check for more pages
        total = data.get("paging", {}).get("total", 0)
        fetched = len(issues)
        if fetched >= total:
            break
        params["p"] += 1
    
    return issues

def fetch_code_context(issue_key, project_key, line, file_path):
    # Fetch surrounding code lines for context (±5 lines)
    try:
        headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}
        params = {
            "key": file_path,
            "from": max(1, line - 5),
            "to": line + 5
        }
        response = requests.get(f"{SONAR_URL}/sources/lines", headers=headers, params=params)
        if response.status_code == 200:
            lines = response.json().get("sources", [])
            context = "\n".join([f"{src.get('line', '')}: {src.get('code', '')}" for src in lines])
            return context.strip() if context else "(No context available)"
        return f"(Failed to fetch context: HTTP {response.status_code})"
    except Exception as e:
        return f"(Failed to fetch context: {str(e)})"

def generate_fix_prompt(issue):
    # Generate a tailored prompt for LLM to suggest fixes
    issue_type = issue.get("type", "UNKNOWN")
    message = issue.get("message", "No description")
    rule_id = issue.get("rule", "UNKNOWN")
    severity = issue.get("severity", "UNKNOWN")
    
    prompts = {
        "CODE_SMELL": {
            "Remove this unused import": "Remove the specified import statement from the file.",
            "A form label must be associated with a control": "Add an `htmlFor` attribute to the label linking it to the corresponding input's `id` in JSX, ensuring accessibility compliance (WCAG 2.1).",
            "Do not use Array index in keys": "Replace array index with a unique identifier (e.g., item ID) for the React key prop to prevent rendering issues.",
            "Extract this nested ternary operation": "Refactor the nested ternary into separate if-statements or a variable assignment for clarity.",
            "Prefer `globalThis` over `window`": "Replace `window` with `globalThis` for better compatibility in Node and browser environments.",
            "Unexpected lexical declaration in case block": "Move the `let` or `const` declaration outside the case block or wrap it in a block scope `{}`."
        },
        "BUG": {
            "Visible, non-interactive elements with click handlers": "Add a `role` attribute (e.g., `button`) and keyboard event listeners (e.g., `onKeyDown`) to ensure accessibility.",
            "Do not add `then` to an object": "Remove the invalid `then` property from the object, as it may cause runtime errors."
        }
    }
    
    default_prompt = "Analyze the issue and provide a concise fix, adhering to best practices for TypeScript and React where applicable."
    return prompts.get(issue_type, {}).get(message, default_prompt)

def format_issues_for_llm(issues):
    # Format issues into detailed markdown code blocks for LLM
    output = []
    for issue in issues:
        file_path = issue.get("component", "unknown")
        line = issue.get("line", "N/A")
        issue_type = issue.get("type", "UNKNOWN")
        severity = issue.get("severity", "UNKNOWN")
        message = issue.get("message", "No description")
        issue_key = issue.get("key", "N/A")
        rule_id = issue.get("rule", "N/A")
        effort = issue.get("effort", "N/A")
        tags = ", ".join(issue.get("tags", [])) or "None"
        status = issue.get("status", "OPEN")
        
        # Extract project and module from component path
        path_parts = file_path.split(":")
        project = path_parts[0] if len(path_parts) > 1 else "N/A"
        module = path_parts[1] if len(path_parts) > 2 else "N/A"
        clean_file = path_parts[-1] if path_parts else file_path
        
        # Fetch code context
        context = fetch_code_context(issue_key, PROJECT_KEY, line if line != "N/A" else 1, file_path) if line != "N/A" else "(No context available)"
        
        # Fetch rule description
        rule_desc = "N/A"
        try:
            headers = {"Authorization": f"Bearer {SONAR_TOKEN}"}
            response = requests.get(f"{SONAR_URL}/rules/show", headers=headers, params={"key": rule_id})
            if response.status_code == 200:
                rule_desc = response.json().get("rule", {}).get("name", "N/A")
        except Exception:
            pass
        
        # Generate LLM fix prompt
        fix_prompt = generate_fix_prompt(issue)
        
        # Build markdown block
        block = f"""```markdown
Issue Key: {issue_key}
Project: {project}
Module: {module}
File: {clean_file}
Line: {line}
Type: {issue_type}
Severity: {severity}
Rule ID: {rule_id}
Rule Description: {rule_desc}
Effort to Fix: {effort}
Tags: {tags}
Status: {status}
Issue: {message}
Code Context:
{context}
LLM Fix Prompt: {fix_prompt}
Suggested Fix: (Provide a fix for the above issue)
```
"""
        output.append(block)
    
    return "\n".join(output) if output else "```markdown\nNo issues found in the project.\n```"

def main():
    print("Fetching SonarCloud issues...")
    issues = fetch_sonarcloud_issues()
    formatted_output = format_issues_for_llm(issues)
    print(formatted_output)

if __name__ == "__main__":
    main()
