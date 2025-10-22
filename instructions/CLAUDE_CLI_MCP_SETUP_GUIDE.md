# Complete Guide: Configure Gmail MCP Server with Claude CLI

## What is MCP?

**MCP (Model Context Protocol)** is a standard that allows Claude to connect to external tools and data sources. Your Gmail MCP server exposes Gmail functionality that Claude can use.

---

## Step-by-Step Configuration Guide

### Step 1: Verify the MCP Server File

Your Gmail MCP server is located at:
```
C:\AIDevelopmentCourse\L12-Agents\L12-Gmail-API-Key\gmail_mcp_server.py
```

**Test it works:**
```bash
cd C:\AIDevelopmentCourse\L12-Agents\L12-Gmail-API-Key
uv run python gmail_mcp_server.py
```

If it starts without errors (it will wait for input), press `Ctrl+C` to stop it. This confirms it's ready!

---

### Step 2: Configure Claude Code

Claude Code uses a configuration file to know which MCP servers to connect to.

#### Option A: Workspace Configuration (Recommended - Already Done!)

I've already created this file for you:
```
.vscode/settings.json
```

**Contents:**
```json
{
  "claudeCode.mcpServers": {
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

This tells Claude Code:
- **Server name:** "gmail"
- **How to start it:** Run `uv run python gmail_mcp_server.py`
- **Where:** In your project directory

#### Option B: Global User Configuration (Optional)

If you want the Gmail MCP server available in ALL your VS Code projects:

1. Open VS Code Settings:
   - Press `Ctrl+,` (Windows/Linux) or `Cmd+,` (Mac)
   - Or click the gear icon ⚙️ → Settings

2. Click the "Open Settings (JSON)" button in the top-right corner
   - This opens your user `settings.json`

3. Add the same configuration:
   ```json
   {
     "claudeCode.mcpServers": {
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

---

### Step 3: Reload VS Code

**This is the crucial step!** VS Code only loads MCP servers at startup.

#### Method 1: Command Palette (Recommended)
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type: `Developer: Reload Window`
3. Press Enter

#### Method 2: Keyboard Shortcut
- Press `Ctrl+R` (Windows/Linux) or `Cmd+R` (Mac)

#### Method 3: Close and Reopen
- Close VS Code completely
- Reopen it in this folder

---

### Step 4: Verify the Connection

After reloading, the Gmail MCP server should be automatically connected.

**How to check:**

1. **Look for MCP indicator** (if available in your VS Code version):
   - Some versions show MCP servers in the status bar or sidebar

2. **Start a new chat with Claude** and ask:
   ```
   List my recent Gmail messages
   ```

3. **If working:** Claude will use the MCP server tools to access your Gmail

4. **If not working:** Continue to troubleshooting below

---

## Step 5: First-Time Gmail Authentication

When you first ask Claude to access Gmail:

1. **Browser window opens** for Google OAuth
2. **Sign in** to your Google account
3. **Grant permission** to read Gmail (read-only)
4. **Credentials saved** to `private/token.pickle`
5. **Future requests** won't need authentication

---

## Available Tools After Setup

Once configured, I (Claude) will have access to:

### 1. **list_gmail_messages**
- List recent emails
- Optional search query
- Default: 10 messages

**Example:**
```
"List my last 20 emails"
```

### 2. **get_gmail_message**
- Get full content of a specific email
- Requires message ID

**Example:**
```
"Get the content of message ID 12345abc"
```

### 3. **search_gmail**
- Search using Gmail query syntax
- Supports complex queries

**Example:**
```
"Search for emails from john@example.com from the last week"
```

### 4. **export_gmail_to_csv**
- Export emails to CSV file
- Optional filtering
- Custom filename

**Example:**
```
"Export my last 50 emails to CSV"
"Export unread emails to unread.csv"
```

---

## Troubleshooting

### Issue 1: "No MCP tools available"

**Solution:**
- Make sure you reloaded VS Code (Step 3)
- Start a **NEW** chat after reloading (old chats won't have access)
- Check `.vscode/settings.json` exists and has correct syntax

### Issue 2: "MCP server failed to start"

**Possible causes:**

1. **Python/uv not found:**
   ```bash
   # Test if uv works
   uv --version

   # Test if Python works
   python --version
   ```

2. **Missing dependencies:**
   ```bash
   cd C:\AIDevelopmentCourse\L12-Agents\L12-Gmail-API-Key
   uv sync
   ```

3. **Wrong file path:**
   - Check the path in `.vscode/settings.json`
   - Make sure `gmail_mcp_server.py` exists

### Issue 3: "Gmail authentication fails"

**Solution:**
1. Make sure `private/` folder exists
2. Make sure OAuth client secret file is in `private/`
3. Delete `private/token.pickle` and try again
4. Check you're using the correct Google account

### Issue 4: "Permission denied" or "Access error"

**Solution:**
- Run VS Code as administrator (if on Windows)
- Check file permissions on `gmail_mcp_server.py`

---

## Testing Your Setup

### Quick Test Commands

After reloading VS Code, start a new chat and try:

1. **Basic test:**
   ```
   List my last 5 Gmail messages
   ```

2. **Search test:**
   ```
   Search my Gmail for emails from the last 3 days
   ```

3. **Export test:**
   ```
   Export my last 10 emails to test_export.csv
   ```

If any of these work, your MCP server is connected! 🎉

---

## Advanced: Multiple MCP Servers

You can configure multiple MCP servers in the same settings file:

```json
{
  "claudeCode.mcpServers": {
    "gmail": {
      "command": "uv",
      "args": ["run", "python", "C:\\path\\to\\gmail_mcp_server.py"]
    },
    "another-server": {
      "command": "node",
      "args": ["C:\\path\\to\\another-server.js"]
    }
  }
}
```

---

## Configuration File Locations

### Workspace Settings (Current Project Only)
```
C:\AIDevelopmentCourse\L12-Agents\L12-Gmail-API-Key\.vscode\settings.json
```

### User Settings (All Projects)
- **Windows:** `%APPDATA%\Code\User\settings.json`
- **Mac:** `~/Library/Application Support/Code/User/settings.json`
- **Linux:** `~/.config/Code/User/settings.json`

---

## Summary Checklist

- [ ] Gmail MCP server file exists and works
- [ ] Configuration added to `.vscode/settings.json` ✅ (Already done!)
- [ ] VS Code reloaded (Ctrl+Shift+P → "Reload Window")
- [ ] New chat started after reload
- [ ] Tested with "List my recent Gmail messages"
- [ ] Gmail OAuth completed (first time only)

---

## Next Steps

1. **Reload VS Code** right now! (Ctrl+Shift+P → "Reload Window")
2. **Start a new chat** with Claude Code
3. **Ask:** "List my recent Gmail messages"
4. **Watch it work!** 🚀

---

## Need Help?

If you're still having issues:

1. Check the VS Code Output panel:
   - View → Output
   - Select "Claude Code" from dropdown

2. Look for error messages about MCP servers

3. Share the error with me and I can help debug!

---

**Your configuration is ready! Just reload VS Code and test it out!** 🎉
