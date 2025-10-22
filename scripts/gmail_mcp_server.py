#!/usr/bin/env python3
"""Gmail MCP Server - Exposes Gmail functionality via Model Context Protocol."""

import asyncio
import os
import pickle
from pathlib import Path
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import mcp.types as types

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import csv
from datetime import datetime

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Paths
BASE_DIR = Path(__file__).parent
TOKEN_PATH = BASE_DIR / 'private' / 'token.pickle'
CLIENT_SECRET_PATH = BASE_DIR / 'private' / 'client_secret_184344902751-bdc92tjt9t9omprtouc2h8koarj8vvbf.apps.googleusercontent.com.json'

# Global Gmail service
_gmail_service = None


def get_gmail_service():
    """Authenticate and return Gmail API service."""
    global _gmail_service

    if _gmail_service:
        return _gmail_service

    creds = None

    # Load existing credentials
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next time
        TOKEN_PATH.parent.mkdir(exist_ok=True)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    _gmail_service = build('gmail', 'v1', credentials=creds)
    return _gmail_service


# Create MCP server
server = Server("gmail-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available Gmail tools."""
    return [
        types.Tool(
            name="list_gmail_messages",
            description="List Gmail messages. Optionally filter with a query string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of messages to return (default: 10)",
                        "default": 10
                    },
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (e.g., 'from:example@gmail.com', 'subject:invoice', 'newer_than:7d')",
                        "default": ""
                    }
                }
            }
        ),
        types.Tool(
            name="get_gmail_message",
            description="Get the full content of a specific Gmail message by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The ID of the Gmail message to retrieve"
                    }
                },
                "required": ["message_id"]
            }
        ),
        types.Tool(
            name="search_gmail",
            description="Search Gmail messages using Gmail query syntax.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (e.g., 'from:example@gmail.com', 'subject:invoice', 'is:unread')"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="export_gmail_to_csv",
            description="Export Gmail messages to a CSV file. Returns the file path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query to filter messages (optional)",
                        "default": ""
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of messages to export (default: 100)",
                        "default": 100
                    },
                    "output_filename": {
                        "type": "string",
                        "description": "Output CSV filename (default: gmail_export_TIMESTAMP.csv)",
                        "default": ""
                    }
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for Gmail operations."""

    if name == "list_gmail_messages":
        max_results = arguments.get("max_results", 10) if arguments else 10
        query = arguments.get("query", "") if arguments else ""

        try:
            service = get_gmail_service()
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return [types.TextContent(type="text", text="No messages found.")]

            output = []
            for msg in messages:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = {h['name']: h['value'] for h in message['payload']['headers']}
                output.append(f"ID: {msg['id']}")
                output.append(f"From: {headers.get('From', 'N/A')}")
                output.append(f"Subject: {headers.get('Subject', 'N/A')}")
                output.append(f"Date: {headers.get('Date', 'N/A')}")
                output.append("-" * 80)

            return [types.TextContent(type="text", text="\n".join(output))]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error listing messages: {str(e)}")]

    elif name == "get_gmail_message":
        if not arguments or "message_id" not in arguments:
            return [types.TextContent(type="text", text="Error: message_id is required")]

        message_id = arguments["message_id"]

        try:
            service = get_gmail_service()
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload']['headers']}

            # Extract body
            def get_body(payload):
                if 'body' in payload and 'data' in payload['body']:
                    return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                elif 'parts' in payload:
                    for part in payload['parts']:
                        body = get_body(part)
                        if body:
                            return body
                return ""

            body = get_body(message['payload'])

            output = []
            output.append(f"From: {headers.get('From', 'N/A')}")
            output.append(f"To: {headers.get('To', 'N/A')}")
            output.append(f"Subject: {headers.get('Subject', 'N/A')}")
            output.append(f"Date: {headers.get('Date', 'N/A')}")
            output.append("-" * 80)
            output.append(body)

            return [types.TextContent(type="text", text="\n".join(output))]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error retrieving message: {str(e)}")]

    elif name == "search_gmail":
        if not arguments or "query" not in arguments:
            return [types.TextContent(type="text", text="Error: query is required")]

        query = arguments["query"]
        max_results = arguments.get("max_results", 20)

        # Reuse the list functionality
        return await handle_call_tool("list_gmail_messages", {"max_results": max_results, "query": query})

    elif name == "export_gmail_to_csv":
        query = arguments.get("query", "") if arguments else ""
        max_results = arguments.get("max_results", 100) if arguments else 100
        output_filename = arguments.get("output_filename", "") if arguments else ""

        # Generate default filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"gmail_export_{timestamp}.csv"

        # Ensure it's in the current directory
        output_path = BASE_DIR / output_filename

        try:
            service = get_gmail_service()
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return [types.TextContent(type="text", text="No messages found to export.")]

            # Collect message data
            email_data = []
            for msg in messages:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                headers = {h['name']: h['value'] for h in message['payload']['headers']}

                # Extract body snippet
                def get_body_snippet(payload):
                    if 'body' in payload and 'data' in payload['body'] and payload['body']['data']:
                        try:
                            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                            # Return first 200 characters
                            return body[:200].replace('\n', ' ').replace('\r', ' ')
                        except:
                            return ""
                    elif 'parts' in payload:
                        for part in payload['parts']:
                            snippet = get_body_snippet(part)
                            if snippet:
                                return snippet
                    return ""

                body_snippet = get_body_snippet(message['payload'])

                email_data.append({
                    'Message ID': msg['id'],
                    'From': headers.get('From', 'N/A'),
                    'To': headers.get('To', 'N/A'),
                    'Subject': headers.get('Subject', 'N/A'),
                    'Date': headers.get('Date', 'N/A'),
                    'Snippet': body_snippet or message.get('snippet', '')
                })

            # Write to CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Message ID', 'From', 'To', 'Subject', 'Date', 'Snippet']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for row in email_data:
                    writer.writerow(row)

            return [types.TextContent(
                type="text",
                text=f"Successfully exported {len(email_data)} messages to: {output_path}\n\nFile contains: Message ID, From, To, Subject, Date, and Snippet (first 200 chars of body)"
            )]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error exporting to CSV: {str(e)}")]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the Gmail MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gmail-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
