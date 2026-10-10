import imaplib
import getpass
import email
from email.header import decode_header
import pandas as pd


# -----------------------------
# LOGIN DETAILS
# -----------------------------

EMAIL = input("Enter your Gmail address: ")
APP_PASSWORD = getpass.getpass("Enter your App Password: ")


# -----------------------------
# CONNECT TO GMAIL
# -----------------------------

print("\nConnecting to Gmail...")

mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)

mail.login(EMAIL, APP_PASSWORD)

print("Successfully connected to Gmail!")


# -----------------------------
# OPEN INBOX
# -----------------------------

mail.select("INBOX")

status, data = mail.search(None, "ALL")

email_ids = data[0].split()

print(f"Total emails found: {len(email_ids)}")


# -----------------------------
# GET LATEST 10 EMAILS
# -----------------------------

latest_emails = email_ids[-10:]

email_data = []


for email_id in reversed(latest_emails):

    status, msg_data = mail.fetch(email_id, "(RFC822)")

    raw_email = msg_data[0][1]

    msg = email.message_from_bytes(raw_email)


    # -------------------------
    # SUBJECT
    # -------------------------

    subject = msg.get("Subject", "")

    decoded_subject = ""

    if subject:

        decoded_parts = decode_header(subject)

        for part, encoding in decoded_parts:

            if isinstance(part, bytes):

                decoded_subject += part.decode(
                    encoding or "utf-8",
                    errors="ignore"
                )

            else:

                decoded_subject += part


    # -------------------------
    # SENDER
    # -------------------------

    sender = msg.get("From", "")


    # -------------------------
    # DATE
    # -------------------------

    date = msg.get("Date", "")


    # -------------------------
    # EMAIL BODY
    # -------------------------

    body = ""

    if msg.is_multipart():

        for part in msg.walk():

            content_type = part.get_content_type()

            content_disposition = str(
                part.get("Content-Disposition")
            )

            if content_type == "text/plain" and "attachment" not in content_disposition:

                payload = part.get_payload(
                    decode=True
                )

                if payload:

                    body = payload.decode(
                        errors="ignore"
                    )

                    break

    else:

        payload = msg.get_payload(
            decode=True
        )

        if payload:

            body = payload.decode(
                errors="ignore"
            )


    # -------------------------
    # STORE DATA
    # -------------------------

    email_data.append({
        "From": sender,
        "Subject": decoded_subject,
        "Date": date,
        "Body": body
    })


# -----------------------------
# CREATE EXCEL FILE
# -----------------------------

df = pd.DataFrame(email_data)

output_file = "gmail_emails.xlsx"

df.to_excel(
    output_file,
    index=False
)

print("\nExcel file created successfully!")

print(f"File: {output_file}")


# -----------------------------
# DISCONNECT
# -----------------------------

mail.logout()

print("Disconnected from Gmail.")