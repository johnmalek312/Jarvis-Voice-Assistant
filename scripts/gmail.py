"""This module provide functions to interact with Gmail or email.
This can be useful for sending emails, reading emails, and managing emails.
This can mark emails as read, important, starred, spam, and more."""

from simplegmail import Gmail, label
from simplegmail.message import Message
from typing import List, Union, Any
import os
from datetime import datetime
from tool_registry import register_tool
# Initialize Gmail client at module level
gmail = Gmail("C:\\Users\\shahi\\Downloads\\Windows AI Assistant\\scripts_data\\client_secret.json", "C:\\Users\\shahi\\Downloads\\Windows AI Assistant\\scripts_data\\gmail_token.json")
@register_tool()
def get_unread_emails(number_of_results: int = 10) -> list[dict]:
    """
    Retrieve a list of unread email summaries from the inbox.
    The result is limited to the specified number of emails.
    """
    gmail.maxResults = number_of_results
    return [snip(email) for email in gmail.get_unread_inbox()]

@register_tool()
def get_all_emails(include_spam_and_trash: bool = True, number_of_results: int = 10) -> list[dict]:
    """
    Retrieve summaries of all emails, optionally including spam and trash.
    The number of emails returned is limited by the provided parameter.
    """
    gmail.maxResults = number_of_results
    return [snip(email) for email in gmail.get_messages(include_spam_trash=include_spam_and_trash)]

@register_tool()
def send_email(to: Union[str, List[str]], subject: str, body: str,
               html: bool = False, cc: List[str] = None,
               bcc: List[str] = None, attachments: List[str] = None) -> None:
    """
    Send an email with provided details such as subject, body, and attachments.
    Supports HTML format along with optional CC and BCC recipients.
    """
    msg_html = body if html else None
    msg_plain = None if html else body

    if isinstance(to, str):
        to = [to]

    for recipient in to:
        gmail.send_message(
            sender="me",
            to=recipient,
            subject=subject,
            msg_plain=msg_plain,
            msg_html=msg_html,
            cc=cc,
            bcc=bcc,
            attachments=attachments
        )

@register_tool()
def search_emails(query: str, max_results: int = 10) -> list[dict]:
    """
    Search for emails matching the given Gmail query syntax.
    Returns a limited number of email summaries based on max_results.
    """
    gmail.maxResults = max_results
    return [snip(email) for email in gmail.get_messages(query=query)]

@register_tool()
def get_starred_emails(max_results: int = 10) -> list[dict]:
    """
    Retrieve summaries of starred emails from the account.
    The number of returned emails is limited by max_results.
    """
    gmail.maxResults = max_results
    return [snip(email) for email in gmail.get_starred_messages()]

@register_tool()
def get_important_emails(max_results: int = 10) -> list[dict]:
    """
    Retrieve summaries of important emails.
    Limits the number of results to the provided max_results value.
    """
    gmail.maxResults = max_results
    return [snip(email) for email in gmail.get_important_messages()]

@register_tool()
def get_sent_emails(max_results: int = 10) -> list[dict]:
    """
    Retrieve summaries of sent emails from the account.
    The number of emails returned is controlled by the max_results parameter.
    """
    gmail.maxResults = max_results
    return [snip(email) for email in gmail.get_sent_messages()]

@register_tool()
def get_draft_emails(max_results: int = 10) -> list[dict]:
    """
    Retrieve summaries of draft emails.
    Results are limited by the specified max_results parameter.
    """
    gmail.maxResults = max_results
    return [snip(email) for email in gmail.get_drafts()]

@register_tool()
def get_spam_emails(max_results: int = 10) -> list[dict]:
    """
    Retrieve summaries of spam emails from the account.
    Limits the number of returned emails using max_results.
    """
    gmail.maxResults = max_results
    return [snip(email) for email in gmail.get_spam_messages()]

@register_tool()
def get_trash_emails(max_results: int = 10) -> list[dict]:
    """
    Retrieve summaries of emails in the trash folder.
    The number of emails returned is limited by the max_results parameter.
    """
    gmail.maxResults = max_results
    return [snip(email) for email in gmail.get_trash_messages()]

@register_tool()
def get_labels() -> list[str]:
    """
    Retrieve all label names from the Gmail account.
    Returns a list of strings representing each label.
    """
    labels: list[str] = [label_.name for label_ in gmail.list_labels()]
    return labels

@register_tool()
def download_attachments(message_id, download_dir: str = "downloaded_email_attachements") -> list[str]:
    """
    Download all attachments for the specified email message.
    Saves files into the designated directory and returns their paths.
    """
    message = get_message_by_id(message_id)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    downloaded_files = []
    for attachment in message.attachments:
        filepath = os.path.join(download_dir, attachment.filename)
        with open(filepath, 'wb') as f:
            f.write(attachment.data)
        downloaded_files.append(filepath)
    return downloaded_files

@register_tool()
def get_emails_by_date(start_date: datetime, end_date: datetime = None) -> list:
    """
    Retrieve email summaries within a specific date range.
    Start date is required, and an optional end date can narrow the search.
    """
    date_query = f"after:{start_date.strftime('%Y/%m/%d')}"
    if end_date:
        date_query += f" before:{end_date.strftime('%Y/%m/%d')}"
    return [snip(email) for email in gmail.get_messages(query=date_query)]

@register_tool()
def mark_as_read(message_id) -> None:
    """
    Mark the specified email as read.
    Removes the 'UNREAD' label from the email.
    """
    get_message_by_id(message_id).remove_label('UNREAD')

@register_tool()
def mark_as_important(message_id) -> None:
    """
    Mark the specified email as important.
    Adds the 'IMPORTANT' label to the email.
    """
    get_message_by_id(message_id).add_label('IMPORTANT')

@register_tool()
def mark_as_not_important(message_id) -> None:
    """
    Remove the important status from the specified email.
    This is achieved by removing the 'IMPORTANT' label.
    """
    get_message_by_id(message_id).remove_label('IMPORTANT')

@register_tool()
def mark_as_unread(message_id) -> None:
    """
    Mark the specified email as unread.
    Achieved by adding the 'UNREAD' label to the email.
    """
    get_message_by_id(message_id).add_label('UNREAD')

@register_tool()
def archive_email(message_id) -> None:
    """
    Archive the specified email by removing it from the inbox.
    This is done by removing the 'INBOX' label.
    """
    get_message_by_id(message_id).remove_label('INBOX')

@register_tool()
def move_to_trash(message_id) -> None:
    """
    Move the specified email to the trash folder.
    Accomplished by adding the 'TRASH' label.
    """
    get_message_by_id(message_id).add_label('TRASH')

@register_tool()
def mark_as_spam(message_id) -> None:
    """
    Mark the specified email as spam.
    Adds the 'SPAM' label to indicate unsolicited content.
    """
    get_message_by_id(message_id).add_label('SPAM')

@register_tool()
def star_email(message_id) -> None:
    """
    Star the specified email to mark it as important.
    Achieved by adding the 'STARRED' label.
    """
    get_message_by_id(message_id).add_label('STARRED')

@register_tool()
def unstar_email(message_id: str) -> None:
    """
    Remove the star from the specified email.
    This is done by removing the 'STARRED' label.
    """
    get_message_by_id(message_id).remove_label('STARRED')

@register_tool()
def get_email_count(label_name: str = 'INBOX') -> int:
    """
    Retrieve the number of emails with the specified label.
    Defaults to counting emails in the inbox.
    """
    lab = label.Label(label_name, label_name)
    messages = gmail.get_messages(labels=[lab])
    return len(messages)

@register_tool()
def get_message_by_id(msg_id: str, user_id: str = 'me', attachments: str = 'reference'):
    """
    Retrieve the full email message by its ID.
    Converts the message to a JSON-friendly format before returning.
    """
    message_ref = {'id': msg_id}  # Create the required reference dictionary
    return message_to_json(gmail._build_message_from_ref(user_id, message_ref, attachments))


def message_to_json(message: Message) -> dict | str:
    """
    Summarize a Gmail Message object to a JSON-friendly format.
    """

    try:
        attachment_summaries = []
        if message.attachments is not None:  # Check if attachments exist
            for attachment in message.attachments:
                attachment_data = attachment.filename if attachment.filename is not None else ""
                attachment_summaries.append(attachment_data)

        summary = {
            'id': message.id if message.id is not None else "",
            'thread_id': message.thread_id if message.thread_id is not None else "",
            'recipient': message.recipient if message.recipient is not None else "",
            'sender': message.sender if message.sender is not None else "",
            'subject': message.subject if message.subject is not None else "",
            'date': message.date if message.date is not None else "",
            'snippet': message.snippet if message.snippet is not None else "",
            'attachments': attachment_summaries,
        }

        return summary

    except AttributeError as e:
        return f"Error: {e} - Ensure you are passing a valid Message object."
    

def snip(message: Message) -> dict:
    """Summarize a Gmail Message object to a JSON-friendly format."""
    label_names = []
    if message.label_ids is not None:  # Check if label_ids exist
        for label_id in message.label_ids:  # you probably meant message.label_ids
            try:  # assuming label_id is Label class object
                label_names.append(label_id.name)
            except AttributeError:  # label_id is just string
                label_names.append(label_id)
    return {
        'id': message.id,
        'recipient': message.recipient,
        'sender': message.sender,
        'subject': message.subject,
        'date': message.date,
        'snippet': message.snippet,
        'labels': label_names,
        'attachments': [attachment.filename
            for attachment in message.attachments
        ]
    }