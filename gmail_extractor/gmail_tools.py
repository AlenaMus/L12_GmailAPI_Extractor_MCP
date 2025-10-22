"""Gmail extraction tools for the ADK agent."""
import os
import pickle
import csv
import base64
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None
    token_path = Path(__file__).parent.parent / 'private' / 'token.pickle'
    client_secret_path = Path(__file__).parent.parent / 'private' / 'client_secret_184344902751-bdc92tjt9t9omprtouc2h8koarj8vvbf.apps.googleusercontent.com.json'

    # Load existing credentials
    if token_path.exists():
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secret_path), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next time
        token_path.parent.mkdir(exist_ok=True)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def list_messages(max_results: int = 10, query: str = "") -> str:
    """
    List Gmail messages.

    Args:
        max_results: Maximum number of messages to return (default: 10)
        query: Gmail search query (e.g., "from:example@gmail.com", "subject:invoice")

    Returns:
        A formatted string with message information
    """
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return "No messages found."

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

        return "\n".join(output)
    except Exception as e:
        return f"Error listing messages: {str(e)}"

def get_message_content(message_id: str) -> str:
    """
    Get the full content of a specific Gmail message.

    Args:
        message_id: The ID of the message to retrieve

    Returns:
        The message content as a string
    """
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
                import base64
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

        return "\n".join(output)
    except Exception as e:
        return f"Error retrieving message: {str(e)}"

def search_messages(query: str, max_results: int = 20) -> str:
    """
    Search Gmail messages using Gmail query syntax.

    Args:
        query: Gmail search query (e.g., "from:example@gmail.com", "subject:invoice", "newer_than:7d")
        max_results: Maximum number of messages to return (default: 20)

    Returns:
        A formatted string with matching messages
    """
    return list_messages(max_results=max_results, query=query)

def export_to_csv(query: str = "", max_results: int = 100, output_filename: str = "") -> str:
    """
    Export Gmail messages to a CSV file.

    Args:
        query: Gmail search query to filter messages (optional)
        max_results: Maximum number of messages to export (default: 100)
        output_filename: Output CSV filename (default: gmail_export_TIMESTAMP.csv)

    Returns:
        Success message with file path
    """
    try:
        # Generate default filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"gmail_export_{timestamp}.csv"

        # Save in parent directory
        output_path = Path(__file__).parent.parent / output_filename

        service = get_gmail_service()
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return "No messages found to export."

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

        return f"Successfully exported {len(email_data)} messages to: {output_path}\n\nFile contains: Message ID, From, To, Subject, Date, and Snippet (first 200 chars of body)"

    except Exception as e:
        return f"Error exporting to CSV: {str(e)}"
