# Gmail MCP Server Setup Instructions

## What We Created

I've created a standalone Gmail MCP (Model Context Protocol) server that exposes three tools:
1. **list_gmail_messages** - List Gmail messages with optional search query
2. **get_gmail_message** - Get full content of a specific message by ID
3. **search_gmail** - Search Gmail using Gmail query syntax

## How to Configure Claude CLI to Use This MCP Server

### Step 1: Open Claude Code Settings

1. Open Claude Code (the app you're using now)
2. Go to Settings (usually Ctrl+, or Cmd+, on Mac)
3. Look for "MCP Servers" or "Model Context Protocol" section

### Step 2: Add the Gmail MCP Server

Add this configuration to your MCP servers:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "C:\\AIDevelopmentCourse\\L12-Agents\\L12-Gmail-API-Key\\gmail_mcp_server.py"
      ]
    }
  }
}
```

**Alternative if uv doesn't work:**

```json
{
  "mcpServers": {
    "gmail": {
      "command": "C:\\AIDevelopmentCourse\\L12-Agents\\L12-Gmail-API-Key\\.venv\\Scripts\\python.exe",
      "args": [
        "C:\\AIDevelopmentCourse\\L12-Agents\\L12-Gmail-API-Key\\gmail_mcp_server.py"
      ]
    }
  }
}
```

### Step 3: Restart Claude Code

After adding the configuration, restart Claude Code for the changes to take effect.

### Step 4: Test the Connection

Once configured, you can ask me (Claude) to:
- "List my recent Gmail messages"
- "Search my Gmail for emails from example@gmail.com"
- "Get the content of Gmail message ID xyz123"

And I'll use the MCP server tools to access your Gmail!

## How It Works

1. When you ask me to access Gmail, I'll call the MCP server tools
2. The MCP server will authenticate using your OAuth credentials from the `private/` folder
3. On first use, it will open a browser for you to authorize Gmail access
4. The credentials are saved in `private/token.pickle` for future use
5. All Gmail access is read-only (no sending or deleting emails)

## Troubleshooting

If the MCP server doesn't work:

1. **Test the server manually:**
   ```bash
   cd C:\AIDevelopmentCourse\L12-Agents\L12-Gmail-API-Key
   uv run python gmail_mcp_server.py
   ```

2. **Check Python path:**
   ```bash
   where python
   ```

3. **Verify dependencies are installed:**
   ```bash
   uv run python -c "import mcp; print('MCP OK')"
   ```

## Available Tools

### list_gmail_messages
- **max_results**: Number of messages to return (default: 10)
- **query**: Gmail search query (optional)

Example queries:
- `from:example@gmail.com`
- `subject:invoice`
- `newer_than:7d`
- `is:unread`

### get_gmail_message
- **message_id**: The Gmail message ID (required)

### search_gmail
- **query**: Gmail search query (required)
- **max_results**: Number of results (default: 20)

## Next Steps

After configuration, simply ask me natural language questions about your Gmail, and I'll use these tools to help you!
