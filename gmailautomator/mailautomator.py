import os
import base64
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def authenticate_gmail():

    creds = None

    # Check whether we already have a token
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    # Refresh existing credentials
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # First-time login
    elif not creds or not creds.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )

        creds = flow.run_local_server(port=0)

        # Save login token
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    return service


def get_email_body(payload):

    body = ""

    if "parts" in payload:

        for part in payload["parts"]:

            if part["mimeType"] == "text/plain":

                data = part["body"].get("data")

                if data:
                    body += base64.urlsafe_b64decode(data).decode(
                        "utf-8",
                        errors="ignore"
                    )

            elif "parts" in part:

                body += get_email_body(part)

    else:

        data = payload.get("body", {}).get("data")

        if data:
            body = base64.urlsafe_b64decode(data).decode(
                "utf-8",
                errors="ignore"
            )

    return body


def get_header(headers, name):

    for header in headers:

        if header["name"].lower() == name.lower():
            return header["value"]

    return ""


def search_emails(service, query):

    results = service.users().messages().list(
        userId="me",
        q=query
    ).execute()

    messages = results.get("messages", [])

    emails = []

    for message in messages:

        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        payload = msg["payload"]

        headers = payload.get("headers", [])

        sender = get_header(headers, "From")
        subject = get_header(headers, "Subject")
        date = get_header(headers, "Date")

        body = get_email_body(payload)

        emails.append({
            "Email ID": message["id"],
            "Sender": sender,
            "Subject": subject,
            "Date": date,
            "Body": body
        })

    return emails


def save_to_excel(emails):

    df = pd.DataFrame(emails)

    df.to_excel(
        "gmail_emails.xlsx",
        index=False
    )

    print(f"Saved {len(df)} emails to gmail_emails.xlsx")


def main():

    print("Connecting to Gmail...")

    service = authenticate_gmail()

    print("Connected successfully.")

    # Search emails from the last 7 days
    query = "newer_than:7d"

    print("Searching emails...")

    emails = search_emails(
        service,
        query
    )

    print(f"Found {len(emails)} emails.")

    save_to_excel(emails)


if __name__ == "__main__":
    main()