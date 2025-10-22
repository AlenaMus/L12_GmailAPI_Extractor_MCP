#!/usr/bin/env python3
"""Fetch 5 unread emails from today and save to CSV."""

import csv
import base64
from pathlib import Path
from datetime import datetime
from gmail_extractor.gmail_tools import get_gmail_service

def fetch_unread_today():
    """Fetch unread emails from today."""
    # Get today's date in Gmail query format
    today = datetime.now().strftime("%Y/%m/%d")

    # Gmail query: unread emails from today
    query = f"is:unread after:{today}"

    output_path = Path("results") / f"unread_emails_today_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId='me',
            maxResults=5,
            q=query
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            print("No unread messages found from today.")
            return

        print(f"Found {len(messages)} unread message(s) from today.")

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
                        return body[:500].replace('\n', ' ').replace('\r', ' ')
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

            print(f"- From: {headers.get('From', 'N/A')}")
            print(f"  Subject: {headers.get('Subject', 'N/A')}")

        # Write to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Message ID', 'From', 'To', 'Subject', 'Date', 'Snippet']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in email_data:
                writer.writerow(row)

        print(f"\n✓ Successfully exported {len(email_data)} messages to: {output_path.absolute()}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fetch_unread_today()
