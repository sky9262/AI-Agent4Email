from typing import Optional, List
from phi.tools import Toolkit
from phi.utils.log import logger
from dotenv import load_dotenv
import os
from email.message import EmailMessage
import smtplib
import ssl

# Load environment variables
load_dotenv()

class CustomEmailTool(Toolkit):
    def __init__(
        self,
        sender_name: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_passkey: Optional[str] = None,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
    ):
        super().__init__(name="email_tools")
        self.sender_name: Optional[str] = sender_name or os.getenv("UserName")
        self.sender_email: Optional[str] = sender_email or os.getenv("EMAIL_ADDRESS")
        self.sender_passkey: Optional[str] = sender_passkey or os.getenv("EMAIL_PASSWORD")
        self.smtp_server: Optional[str] = smtp_server or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port: Optional[int] = smtp_port or int(os.getenv("SMTP_PORT", 465)) 
        self.register(self.send_email)

        # Debugging logs for environment variables
        logger.debug(f"Sender Name: {self.sender_name}")
        logger.debug(f"Sender Email: {self.sender_email}")
        logger.debug(f"SMTP Server: {self.smtp_server}")
        logger.debug(f"SMTP Port: {self.smtp_port}")

    def send_email(self, *, to: List[str], subject: str, body: str) -> str:
        """Emails the user with the given subject and body.

        :param to: List of recipient email addresses.
        :param subject: The subject of the email.
        :param body: The body of the email.
        :return: "success" if the email was sent successfully, "error: [error message]" otherwise.
        """
        if not to:
            return "error: No recipient email provided"
        if not self.sender_name:
            return "error: No sender name provided"
        if not self.sender_email:
            return "error: No sender email provided"
        if not self.sender_passkey:
            return "error: No sender passkey provided"

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.sender_email}>"
        msg["To"] = ", ".join(to)
        msg.set_content(body)
        
        logger.info(f"Sending Email to {', '.join(to)}")
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.starttls(context=context)
                smtp.login(self.sender_email, self.sender_passkey)
                smtp.send_message(msg)
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return f"error: {e}"
        return "email sent successfully"


# Integration with Agent
from phi.agent import Agent
from phi.model.groq import Groq

email_tool = CustomEmailTool()

agent = Agent(
    name="Email Manager",
    agent_id="email-manager",
    model=Groq(id="gemma2-9b-it"),
    tools=[email_tool],
    markdown=True,
    show_tool_calls=True,
    debug_mode=True,  # Enable debugging
    instructions=[
        "You are an expert at managing and sending emails.",
        "You can:",
        "1. Send emails dynamically with recipient(s), subject, and body.",
        "",
        "Guidelines:",
        "- Specify recipient(s) as a list of email addresses.",
        "- Provide a valid subject and body for the email.",
        "- Do not include sender email in the function arguments.",
        "- Confirm successful email sending or handle errors gracefully.",
        "",
        "The `send_email` function requires:",
        "- `to`: List of recipient email addresses.",
        "- `subject`: The email subject.",
        "- `body`: The email body.",
    ],
)

# Example Usage
# agent.print_response("Send an email to ['akash.kumar@roboken2.com'] with subject 'Hello' and body 'This is a test email.'")
