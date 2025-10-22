#!/usr/bin/env python3
"""Create CSV from saved email files."""

import csv
import sys
from pathlib import Path
import re

def extract_email_info(file_path):
    """Extract email information from a saved email text file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract fields using regex
    message_id_match = re.search(r'^Message ID: (.+)$', content, re.MULTILINE)
    from_match = re.search(r'^From: (.+)$', content, re.MULTILINE)
    to_match = re.search(r'^To: (.+)$', content, re.MULTILINE)
    subject_match = re.search(r'^Subject: (.+)$', content, re.MULTILINE)
    date_match = re.search(r'^Date: (.+)$', content, re.MULTILINE)

    # Extract body (everything after "EMAIL BODY:" and before final separator)
    body_match = re.search(r'EMAIL BODY:\n\n(.+?)\n={80}', content, re.DOTALL)
    body = body_match.group(1).strip() if body_match else ''

    # Get first 200 chars of body as snippet
    snippet = body[:200].replace('\n', ' ').replace('\r', ' ') if body else ''

    return {
        'Message ID': message_id_match.group(1) if message_id_match else 'N/A',
        'From': from_match.group(1) if from_match else 'N/A',
        'To': to_match.group(1) if to_match else 'N/A',
        'Subject': subject_match.group(1) if subject_match else 'N/A',
        'Date': date_match.group(1) if date_match else 'N/A',
        'Snippet': snippet
    }

def create_csv_from_pattern(pattern, output_csv):
    """Create CSV from email files matching a pattern."""
    results_dir = Path(__file__).parent / 'results'

    # Find all matching files
    email_files = sorted(results_dir.glob(pattern))

    if not email_files:
        print(f"No email files found matching pattern: {pattern}")
        return

    print(f"Found {len(email_files)} email file(s) matching pattern: {pattern}")

    # Extract data from all files
    email_data = []
    for email_file in email_files:
        try:
            info = extract_email_info(email_file)
            email_data.append(info)
            print(f"  Processed: {email_file.name}")
        except Exception as e:
            print(f"  Error processing {email_file.name}: {e}")

    # Write to CSV
    output_path = results_dir / output_csv
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Message ID', 'From', 'To', 'Subject', 'Date', 'Snippet']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in email_data:
            writer.writerow(row)

    print(f"\nSuccessfully created CSV: {output_path}")
    print(f"Total emails: {len(email_data)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_csv_from_emails.py <file_pattern> <output_csv>")
        print("Example: python create_csv_from_emails.py 'lior_frnkl_*.txt' lior_emails.csv")
        sys.exit(1)

    pattern = sys.argv[1]
    output_csv = sys.argv[2]

    create_csv_from_pattern(pattern, output_csv)
