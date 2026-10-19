import os
from dataclasses import dataclass
from typing import Optional
import base64
from email.utils import parseaddr

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from ..utils.env import load_env
load_env()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def connect_gmail():
    creds = None

    # Reuse previously authorized credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json", SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = {
                "installed": {
                    "client_id": os.getenv("GMAIL_CLIENT_ID"),
                    "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"]
                }
            }

            if not client_config["installed"]["client_id"]:
                raise ValueError("GMAIL_CLIENT_ID is missing from .env")

            if not client_config["installed"]["client_secret"]:
                raise ValueError("GMAIL_CLIENT_SECRET is missing from .env")

            flow = InstalledAppFlow.from_client_config(
                client_config, SCOPES
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def decode_body(data: str) -> str:
    if not data:
        return ""
    padding = "=" * (-len(data) % 4)
    decoded = base64.urlsafe_b64decode(data + padding)
    return decoded.decode("utf-8", errors="replace")


def extract_bodies(payload: dict) -> dict:
    bodies = {"text": [], "html": []}

    def walk(part: dict) -> None:
        mime_type = part.get("mimeType", "")
        body_data = part.get("body", {}).get("data")

        if body_data:
            content = decode_body(body_data)

            if mime_type == "text/plain":
                bodies["text"].append(content)
            elif mime_type == "text/html":
                bodies["html"].append(content)

        for child in part.get("parts", []):
            walk(child)

    walk(payload)
    return {
        "text": "\n".join(bodies["text"]),
        "html": "\n".join(bodies["html"]),
    }


@dataclass
class Email:
    id: str
    thread_id: Optional[str]
    sender: str
    sender_name: str
    sender_email: str
    to: str
    subject: str
    date: str
    text: str
    html: str
    snippet: str
    index: int = 0

def get_emails() -> list[Email]:
    service = connect_gmail()

    emails: list[Email] = []

    results = service.users().messages().list(
        userId="me",
        maxResults=30,
    ).execute()

    for message in results.get("messages", []):
        data = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full",
        ).execute()

        headers = {
            h["name"].lower(): h["value"]
            for h in data.get("payload", {}).get("headers", [])
        }

        bodies = extract_bodies(data.get("payload", {}))
        sender = headers.get("from", "Unknown")

        email = Email(
            id=data["id"],
            thread_id=data.get("threadId"),
            sender=sender,
            sender_name=parseaddr(sender)[0],
            sender_email=parseaddr(sender)[1],
            to=headers.get("to", ""),
            subject=headers.get("subject", "No subject"),
            date=headers.get("date", ""),
            text=bodies["text"],
            html=bodies["html"],
            snippet=data.get("snippet", ""),
        )

        emails.append(email)

    return emails

def get_full_email(indexes: list[int]) -> str:
    emails = get_emails()

    lines = []
    for index, email in enumerate(emails):
        email.index = index
        if index in indexes:
            lines.append(
                f"id: {index}\n"
                f"sender_email: {email.sender_email}\n"
                f"subject: {email.subject.replace("Fwd:", "")}\n"
                f"body: {email.text}"
            )

    return "\n".join(lines)

def get_headers_email() -> str:
    emails = get_emails()

    lines = []
    for index, email in enumerate(emails):
        email.index = index
        lines.append(
            f"id: {index}\n"
            f"sender_email: {email.sender_email}\n"
            f"subject: {email.subject.replace("Fwd", "")}\n"
        )

    return "\n".join(lines)

def get_tool_usage_prompt() -> str:
    return "".join(
        "Tool for gathering users email information, two functions"
        "'tool:get_headers_email()' can be used to get metadata data about emails their (id, sender_email, subject). Example usage 'tool:get_headers_email()'"
        "'tool:get_full_email(id1, id2,...)' can be used to get full data about emails their (id, sender_email, subject, text body). Example usage 'tool:get_full_email(2, 4, 5, 6)'"
    )

def get_tools() -> list[dict]:
    return [
        {"command": "get_headers_email", "args": [], "func": get_headers_email},
        {"command": "get_full_email", "args": ["int..."], "func": get_full_email}
    ]

if __name__ == "__main__":
    get_headers_email()
