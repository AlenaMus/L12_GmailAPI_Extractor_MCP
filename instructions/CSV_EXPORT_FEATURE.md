# Gmail CSV Export Feature - Added!

## What's New

I've added CSV export functionality to both:
1. **Gmail MCP Server** (for Claude CLI)
2. **Gmail Web Agent** (for the web UI at http://127.0.0.1:8000)

## New Tool: `export_gmail_to_csv`

### Features:
- Export Gmail messages to CSV format
- Optional search query filtering
- Configurable number of results
- Custom filename support
- Automatic timestamp in default filenames

### CSV Columns:
1. **Message ID** - Unique Gmail message identifier
2. **From** - Sender email address
3. **To** - Recipient email address
4. **Subject** - Email subject line
5. **Date** - Email date/time
6. **Snippet** - First 200 characters of email body

## How to Use

### For Claude CLI (MCP Server):
After reloading VS Code, you can ask me:
- "Export my last 50 Gmail messages to CSV"
- "Export emails from the last week to CSV"
- "Search for emails from john@example.com and export to CSV"
- "Export unread emails to a file called unread_emails.csv"

### For Web Agent (http://127.0.0.1:8000):
Ask the agent in the web UI:
- "Export my emails to CSV"
- "Export emails with subject containing 'invoice' to CSV"
- "Export the last 100 messages"

## Parameters

### `query` (optional)
- Gmail search query to filter messages
- Examples: `"from:example@gmail.com"`, `"subject:invoice"`, `"newer_than:7d"`, `"is:unread"`
- Default: "" (all messages)

### `max_results` (optional)
- Maximum number of messages to export
- Default: 100
- Range: 1-500 (Gmail API limit)

### `output_filename` (optional)
- Custom filename for the CSV file
- Default: `gmail_export_YYYYMMDD_HHMMSS.csv`
- File will be saved in the project directory

## Example Usage

### Basic Export:
```
"Export my last 50 emails to CSV"
```
Result: `gmail_export_20251022_101530.csv` with 50 most recent messages

### Filtered Export:
```
"Export all emails from the last 7 days to weekly_emails.csv"
```
Result: `weekly_emails.csv` with emails from last week

### Search and Export:
```
"Find all emails with 'receipt' in the subject and export them"
```
Result: CSV file with all matching emails

## File Location

CSV files are saved in:
```
C:\AIDevelopmentCourse\L12-Agents\L12-Gmail-API-Key\
```

## Notes

- Exports are read-only (no emails are modified or deleted)
- Large exports may take a few moments to complete
- Body content is limited to first 200 characters (snippet)
- All text is UTF-8 encoded for international character support
- Special characters in CSV are properly escaped

## Next Steps

1. **Reload VS Code** to load the updated MCP server
2. Ask me to export your Gmail messages!
3. Open the CSV file in Excel, Google Sheets, or any CSV viewer

Enjoy your new CSV export feature! 📊
