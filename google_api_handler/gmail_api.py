import os.path
import time
from typing import Any, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
# TODO: Elevated scope. Will be reduced in the production phase
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailClient:
    def __init__(self, creds_path="oauth_creds.json", token_path="token.json"):
        self.creds_path = creds_path
        self.token_path = token_path
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.creds_path, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())
        self.service = build("gmail", "v1", credentials=self.creds)

    def get_service(self) -> Any:
        return self.service


class GmailMailFetcher:
    """Fetches subjects or snippets from mails by sender."""

    def __init__(self, client: GmailClient, userId: str = "me"):
        self.service = client.get_service()
        self.userId = userId

    def list_labels(self) -> List[str]:
        results = self.service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        return [label["name"] for label in labels]

    def get_messages_by_id(
        self,
        msg_id: str,
        format: Optional[str] = None,
        metadata: list[str] | None = None,
    ) -> dict:
        results = (
            self.service.users()
            .messages()
            .get(userId=self.userId, id=msg_id, format=format, metadataHeaders=metadata)
            .execute()
        )
        return results

    def list_all_messages(self, sender_email: str) -> List:
        response = (
            self.service.users()
            .messages()
            .list(userId=self.userId, q=f"from:{sender_email}")
            .execute()
        )
        return response.get("messages", [])

    def get_subjects_from_sender(self, sender_email: str) -> List[Optional[str]]:
        messages = self.list_all_messages(sender_email)
        subjects = []
        for message in messages:
            msg = self.get_messages_by_id(
                msg_id=message["id"],
                format="metadata",
                metadata=["Subject"],
            )
            headers = msg["payload"].get("headers", [])
            subject = next(
                (h["value"] for h in headers if h["name"] == "Subject"), None
            )
            subjects.append(subject)
        return subjects

    def get_snippet_from_sender(self, sender_email: str) -> List[str]:
        messages = self.list_all_messages(sender_email)
        snippets = []
        for message in messages:
            msg = self.get_messages_by_id(msg_id=message["id"])
            snippet = msg.get("snippet", "")

            snippets.append(snippet)
        return snippets

    def poll_new_subjects_from_sender(self, sender_email: str, poll_interval: int = 15):
        seen_message_ids = set()
        print(
            f"Polling for new emails from {sender_email} every {poll_interval} seconds..."
        )
        while True:
            try:
                messages = self.list_all_messages(sender_email)
                new_messages = [
                    msg for msg in messages if msg["id"] not in seen_message_ids
                ]
                for msg in new_messages:
                    msg_detail = self.get_messages_by_id(
                        msg_id=msg["id"],
                        format="metadata",
                        metadata=["Subject"],
                    )
                    headers = msg_detail["payload"].get("headers", [])
                    subject = next(
                        (h["value"] for h in headers if h["name"] == "Subject"),
                        "No Subject",
                    )
                    print(f"New mail from {sender_email}: {subject}")
                    seen_message_ids.add(msg["id"])

                time.sleep(poll_interval)

            except HttpError as error:
                print(f"An error occurred: {error}")
                time.sleep(poll_interval)


if __name__ == "__main__":
    try:
        client = GmailClient()

        # # List all labels
        # label_helper = GmailMailFetcher(client)
        # labels = label_helper.list_labels()
        # print("Labels:")
        # for label in labels:
        #     print(label)

        # # List all subjects from a particular sender
        # sender_email = "caralerts@intellicar.in"  # replace with desired sender
        # mail_helper = GmailMailFetcher(client)
        # subjects = mail_helper.get_subjects_from_sender(sender_email)
        # print(f"\nSubjects from {sender_email}:")
        # for subj in subjects:
        #     print(subj)

        # List all snippets from a particular sender
        sender_email = "caralerts@intellicar.in"  # replace with desired sender
        mail_helper = GmailMailFetcher(client)
        snippets = mail_helper.get_snippet_from_sender(sender_email)
        print(f"\nSnippets from {sender_email}:")
        for snippet in snippets:
            print(snippet)

        # # Lists a new msg if the sender has sent the mail after the desired time(mentioned in poll_interval)
        # sender_email = "nagendrar@rideriver.com"  # Replace with desired sender
        # client = GmailClient()
        # mail_helper = GmailMailFetcher(client)
        # mail_helper.poll_new_subjects_from_sender(sender_email, poll_interval=15)

        # sender_email = "nagendrar@rideriver.com"  # Replace with desired sender
        # client = GmailClient()
        # mail_helper = GmailMailFetcher(client)
        # # # snippets = mail_helper.get_snippet_from_sender(sender_email)
        # t_id = "199507d080c766f3"
        # # # mail_helper.get_messages_by_id(t_id)
        # print(mail_helper.list_all_messages(sender_email))
        # # print(f"\nSnippets from {sender_email}:")
        # # for snippet in snippets:
        # #     print(snippet)

    except HttpError as error:
        print(f"An error occurred: {error}")
