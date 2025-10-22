#!/usr/bin/env python3
"""Script to save emails with a specific tag/label to the results directory."""

import os
import pickle
import json
import sys
import argparse
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from datetime import datetime

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Paths
BASE_DIR = Path(__file__).parent
TOKEN_PATH = BASE_DIR / 'private' / 'token.pickle'
CLIENT_SECRET_PATH = BASE_DIR / 'private' / 'client_secret_184344902751-bdc92tjt9t9omprtouc2h8koarj8vvbf.apps.googleusercontent.com.json'
RESULTS_DIR = BASE_DIR / 'results'

def get_gmail_service():
    """Authenticate and return Gmail API service."""
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

    return build('gmail', 'v1', credentials=creds)

def get_body(payload):
    """Recursively extract email body from payload."""
    if 'body' in payload and 'data' in payload['body'] and payload['body']['data']:
        try:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
        except:
            return ""
    elif 'parts' in payload:
        body_parts = []
        for part in payload['parts']:
            body = get_body(part)
            if body:
                body_parts.append(body)
        return '\n'.join(body_parts)
    return ""

def save_emails_with_query(query, max_results=10, output_prefix='email'):
    """Search for emails with custom query and save them.

    Args:
        query: Gmail search query
        max_results: Maximum number of emails to save (default: 10)
        output_prefix: Prefix for output filenames (default: 'email')
    """
    try:
        # Create results directory if it doesn't exist
        RESULTS_DIR.mkdir(exist_ok=True)

        # Get Gmail service
        service = get_gmail_service()

        print(f"Searching for emails with query: {query}")

        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            print(f"No messages found with query: {query}")
            return

        print(f"Found {len(messages)} email(s). Saving to {RESULTS_DIR}...")

        # Process each message
        for idx, msg in enumerate(messages, 1):
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload']['headers']}

            # Extract body
            body = get_body(message['payload'])

            # Create filename
            subject = headers.get('Subject', 'No Subject').replace('/', '_').replace('\\', '_')
            # Limit subject length for filename
            subject = subject[:50] if len(subject) > 50 else subject
            filename = f"{output_prefix}_{idx}_{msg['id']}.txt"
            filepath = RESULTS_DIR / filename

            # Prepare email content
            email_content = []
            email_content.append("=" * 80)
            email_content.append(f"EMAIL {idx} OF {len(messages)}")
            email_content.append("=" * 80)
            email_content.append(f"Message ID: {msg['id']}")
            email_content.append(f"From: {headers.get('From', 'N/A')}")
            email_content.append(f"To: {headers.get('To', 'N/A')}")
            email_content.append(f"Subject: {headers.get('Subject', 'N/A')}")
            email_content.append(f"Date: {headers.get('Date', 'N/A')}")
            email_content.append("=" * 80)
            email_content.append("\nEMAIL BODY:\n")
            email_content.append(body)
            email_content.append("\n" + "=" * 80)

            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(email_content))

            print(f"[OK] Saved email {idx}: {filepath}")
            try:
                print(f"  Subject: {headers.get('Subject', 'N/A')}")
                print(f"  From: {headers.get('From', 'N/A')}")
            except UnicodeEncodeError:
                print(f"  Subject: [Contains special characters]")
                print(f"  From: [Contains special characters]")
            print()

        print(f"\nSuccessfully saved {len(messages)} email(s) to: {RESULTS_DIR}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

def save_emails_with_tag(tag, max_results=3, output_prefix=None):
    """Search for emails with specified label and save them.

    Args:
        tag: The Gmail label/tag to search for
        max_results: Maximum number of emails to save (default: 3)
        output_prefix: Prefix for output filenames (default: uses tag name)
    """
    try:
        # Create results directory if it doesn't exist
        RESULTS_DIR.mkdir(exist_ok=True)

        # Get Gmail service
        service = get_gmail_service()

        # Search for emails with specified label
        # Gmail uses 'label:labelname' to search by label
        query = f'label:{tag}'

        print(f"Searching for emails with query: {query}")

        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            print(f"No messages found with '{tag}' tag.")
            return

        print(f"Found {len(messages)} email(s) with '{tag}' tag. Saving to {RESULTS_DIR}...")

        # Use tag name as prefix if not specified
        if output_prefix is None:
            output_prefix = tag

        # Process each message
        for idx, msg in enumerate(messages, 1):
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in message['payload']['headers']}

            # Extract body
            body = get_body(message['payload'])

            # Create filename
            subject = headers.get('Subject', 'No Subject').replace('/', '_').replace('\\', '_')
            # Limit subject length for filename
            subject = subject[:50] if len(subject) > 50 else subject
            filename = f"{output_prefix}_email_{idx}_{msg['id']}.txt"
            filepath = RESULTS_DIR / filename

            # Prepare email content
            email_content = []
            email_content.append("=" * 80)
            email_content.append(f"EMAIL {idx} OF {len(messages)}")
            email_content.append("=" * 80)
            email_content.append(f"Message ID: {msg['id']}")
            email_content.append(f"From: {headers.get('From', 'N/A')}")
            email_content.append(f"To: {headers.get('To', 'N/A')}")
            email_content.append(f"Subject: {headers.get('Subject', 'N/A')}")
            email_content.append(f"Date: {headers.get('Date', 'N/A')}")
            email_content.append("=" * 80)
            email_content.append("\nEMAIL BODY:\n")
            email_content.append(body)
            email_content.append("\n" + "=" * 80)

            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(email_content))

            print(f"[OK] Saved email {idx}: {filepath}")
            try:
                print(f"  Subject: {headers.get('Subject', 'N/A')}")
                print(f"  From: {headers.get('From', 'N/A')}")
            except UnicodeEncodeError:
                print(f"  Subject: [Contains special characters]")
                print(f"  From: [Contains special characters]")
            print()

        print(f"\nSuccessfully saved {len(messages)} email(s) to: {RESULTS_DIR}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Save emails with a specific Gmail label/tag to the results directory.'
    )
    parser.add_argument(
        'tag',
        type=str,
        nargs='?',
        default=None,
        help='Gmail label/tag to search for (e.g., payments, aidevelopment). Optional if using --query'
    )
    parser.add_argument(
        '-n', '--max-results',
        type=int,
        default=3,
        help='Maximum number of emails to save (default: 3)'
    )
    parser.add_argument(
        '-p', '--prefix',
        type=str,
        default=None,
        help='Prefix for output filenames (default: uses tag name)'
    )
    parser.add_argument(
        '-q', '--query',
        type=str,
        default=None,
        help='Custom Gmail search query (e.g., "is:unread after:2025/10/19")'
    )

    args = parser.parse_args()

    # If custom query provided, use it directly
    if args.query:
        save_emails_with_query(
            query=args.query,
            max_results=args.max_results,
            output_prefix=args.prefix or 'email'
        )
    elif args.tag:
        save_emails_with_tag(
            tag=args.tag,
            max_results=args.max_results,
            output_prefix=args.prefix
        )
    else:
        parser.error("Either 'tag' or '--query' must be provided")
