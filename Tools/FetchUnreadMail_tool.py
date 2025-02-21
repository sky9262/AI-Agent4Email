from typing import Optional
from phi.tools import Toolkit
from phi.utils.log import logger
from dotenv import load_dotenv
import os
from email.header import decode_header
import imaplib
import re
import email

# Load environment variables
load_dotenv()


class FetchUnreadEmailTool(Toolkit):
    def __init__(
        self,
        email_address: Optional[str] = None,
        email_password: Optional[str] = None,
        imap_server: Optional[str] = None,
        imap_port: Optional[int] = None,
    ):
        super().__init__(name="unread_email_tool")
        self.email_address: Optional[str] = email_address or os.getenv("EMAIL_ADDRESS")
        self.email_password: Optional[str] = email_password or os.getenv("EMAIL_PASSWORD")
        self.imap_server: Optional[str] = imap_server or os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.imap_port: Optional[int] = imap_port or int(os.getenv("IMAP_PORT", 993))

        # Register the tool
        self.register(self.fetch_unread_emails)

        # Debugging logs for environment variables
        logger.debug(f"Email Address: {self.email_address}")
        logger.debug(f"IMAP Server: {self.imap_server}")
        logger.debug(f"IMAP Port: {self.imap_port}")

    def fetch_unread_emails(self) -> str:
        """
        Fetch unread emails from the mailbox and return them as a formatted string.
        """
        unread_emails = []
        try:
            # Connect to the IMAP server
            with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as mail:
                mail.login(self.email_address, self.email_password)
                mail.select("inbox")

                # Search for unread emails
                status, messages = mail.search(None, "UNSEEN")
                if status != "OK":
                    return "Failed to fetch unread emails."

                # Fetch each unread email
                for num in messages[0].split():
                    status, msg_data = mail.fetch(num, "(RFC822)")
                    if status != "OK":
                        continue
                    
                    
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            email_from = decode_header(msg["From"])[0][0]
                            email_subject = decode_header(msg["Subject"])[0][0]
                            if isinstance(email_from, bytes):
                                email_from = email_from.decode()
                            if isinstance(email_subject, bytes):
                                email_subject = email_subject.decode()

                            # Extracting the name and email using regex
                            match = re.match(r"(.*) <(.*)>", email_from)
                            SenderName = match.group(1) if match else None
                            SenderEmail = match.group(2) if match else None

                            email_body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        email_body = part.get_payload(decode=True).decode()
                                        break
                            else:
                                email_body = msg.get_payload(decode=True).decode()

                            unread_emails.append([SenderName, SenderEmail,email_subject,email_body])
        except Exception as e:
            logger.error(f"Error fetching unread emails: {e}")
            return f"Error fetching unread emails: {e}"

        return unread_emails if unread_emails else "No unread emails found."


# Integration with Agent
from phi.agent import Agent
from phi.model.groq import Groq

unread_email_tool = FetchUnreadEmailTool()

agent = Agent(
    name="Unread Email Checker",
    agent_id="unread-email-checker",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[unread_email_tool],
    markdown=True,
    show_tool_calls=False,
    debug_mode=False,  # Enable debugging
    instructions=[
        "You are an expert at fetching unread emails.",
        "When the user asks to fetch unread emails, call the `fetch_unread_emails` function exactly once.",
        # "Return the result as-is without any further processing or re-calling the function.",
        "If there are no unread emails, simply return 'No unread emails found.'",
        "return in table format 'Sender Name', 'Sender Email', 'subject', 'body'"
    ],
)

# Example Usage
# agent.print_response("fetch unread emails")
