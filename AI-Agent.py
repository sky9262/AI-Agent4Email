import os
import time
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.groq import Groq
# Import Custom Email Tools
from Tools.SendEmail_tool import CustomEmailTool 
from Tools.FetchUnreadMail_tool import FetchUnreadEmailTool  
from Tools.zoom_tool import CustomZoomTool
from Tools.calcom_tool import CalCom 

# Load environment variables
load_dotenv()

UserName = os.getenv("UserName")
EMAIL_LANGUAGE = os.getenv("EMAIL_LANGUAGE")

# Instantiate Zoom Tool
zoom_tool = CustomZoomTool(
    account_id=os.getenv("ZOOM_ACCOUNT_ID"),
    client_id=os.getenv("ZOOM_CLIENT_ID"),
    client_secret=os.getenv("ZOOM_CLIENT_SECRET"),
)


# Instantiate SendEmail Tool
SendEmail_tool = CustomEmailTool(
    smtp_server=os.getenv("SMTP_SERVER"),
    sender_email=os.getenv("EMAIL_ADDRESS"),
    sender_passkey=os.getenv("EMAIL_PASSWORD"),
)

# Instantiate FetchUnreadMail Tool
FetchUnreadEmail_tool = FetchUnreadEmailTool(
    imap_server=os.getenv("IMAP_SERVER"),
    imap_port=int(os.getenv("IMAP_PORT", 993)),
    email_address=os.getenv("EMAIL_ADDRESS"),
    email_password=os.getenv("EMAIL_PASSWORD"),
)

# Instantiate CalCom Tool
calcom_tool = CalCom(
    api_key=os.getenv("CALCOM_API_KEY"),
    event_type_id=int(os.getenv("CALCOM_EVENT_TYPE_ID", "0")),
    user_timezone=os.getenv("CALCOM_USER_TIMEZONE", "Asia/Tokyo"),
)

# Use OpenAI ChatGPT API
from typing import List, Dict
import openai

class OpenAIChatModel:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        openai.api_key = self.api_key

    def __call__(self, prompt: str) -> str:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a meeting assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message["content"]

# Create Agent with all tools
agent = Agent(
    name="My Meeting Agent",
    agent_id="meeting-agent",
    chat_model=OpenAIChatModel(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4"),
    tools=[
        zoom_tool,
        calcom_tool,
        SendEmail_tool,  # Register SendEmail Tool
        FetchUnreadEmail_tool,  # Register FetchUnreadMail Tool
    ],
    instructions=[
        "You are responsible for handling meeting requests, scheduling, and notifications. Follow these steps:",

        "Step 1: Use 'calcom_tool' to find available slots for the requested date range.",


        "Case 1: If the requested meeting time is not available, If a meeting request falls on a weekend, a Japan national holiday, or during restricted weekday hours (before 9 AM, between 1 PM and 2 PM, or after 6 PM)",
        "   Step 2: Extract the first available slot from the response.",
        "   Step 3: generate an email with politely decline the email request with proper reason and appolise.",
        "   Step 4: Send an email to the sender, providing a clear reason and expressing regret in a well-mannered tone.",
        "   Step 5: Include three alternative time slots in the reply to the email.",

        "Case 2: If the requested meeting time is available",
        "   Step 1: Use 'zoom_tool' to schedule a Zoom meeting for the booked time.",
        "   Step 2: Extract the Zoom link from the response.",
        "   Step 3: Use 'calcom_tool' to create a booking with the extracted slot, Zoom link, attendee name, and email address.",
        "           **Note:** Ensure to include zoom link while using calcom_tool.",
        "   Step 4: Use 'SendEmail_tool' to send a confirmation email to the sender.",
        "   Step 5: Replace placeholders like [start_time] and [join_url] with actual values from tool responses.",
        "   Step 6: Before sending the email, always use 'email_metadata'.",
        "   Step 7: Follow the email text language from the metadata and ensure placeholders like '[Your Zoom Meeting URL]' or '[Meeting Time]' are replaced with actual details from tool responses.",
        "   Step 8: Use a beautiful format for the email body using markdown or other formats supported across devices and email applications.",

        "Important Guidelines:",
        "   - If you get an email from hello@cal.com or cal.com or any email like noreply@... just ignore those emails.",
        "   - Always make use that the placeholders like '[Your Zoom Meeting URL]' or '[Meeting Time]' are replaced with actual details from tool responses.",
        "   - If any step fails (e.g., no available slots or booking creation error), inform the user politely.",
        "   - Use clear, professional, and polite language in all communications.",
        "   - When scheduling a meeting, confirm the proposed time and date with the user if there is any uncertainty.",
        "use this email_template""""

[相手の名前] 様

お世話になっております。[私の名前] です。

[メールの目的や内容を簡潔に述べる]

[詳細な説明や必要な情報を提供する]

何卒よろしくお願い申し上げます。

[私の名前]
""",

f"IMPORTANT: Before sending email Always replace the placeholders like [相手の名前] with SenderName [私の名前] or [Your Name] with {UserName} from the env.",
"IMPORTANT: Do not ask for permission like 'Shall I proceed to send this email?', because the agent is responsible for sending emails user will not be able to respond to this question.",
"IMPORTANT: Always reply with the same language as the email received.",
    ],
    markdown=True,
    show_tool_calls=False,
    debug_mode=False,
)


def fetch_unread_emails_with_retry(retries=3, delay=5):
    for attempt in range(retries):
        try:
            unread_emails = FetchUnreadEmail_tool.fetch_unread_emails()
            if unread_emails in ["No unread emails found.", "Error fetching unread emails: 'utf-8' codec can't decode byte 0xe3 in position 0: invalid continuation byte"]:
                print("No unread emails found.")
                return []
            else:
                return unread_emails
        except Exception as e:
            print(f"Error fetching unread emails: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Exiting.")
                return []
            

# Loop to check emails every 30 seconds
def process_emails():
    while True:
        print("Checking for unread emails...")
        
        # Fetch unread emails
        unread_emails = fetch_unread_emails_with_retry()
        
        # Check if the returned result is a valid list of dictionaries
        if (unread_emails == "No unread emails found.") or (unread_emails == "Error fetching unread emails: 'utf-8' codec can't decode byte 0xe3 in position 0: invalid continuation byte"):
           print("No unread emails found.")
        else:
            print(f"Unread emails: {unread_emails}")
            for email in unread_emails:
                prompt = (
                    f"The following email was received:\n\n"
                    f"**Sender Name:** {email[0]}\n"
                    f"**Sender Email:** {email[1]}\n"
                    f"**Subject:** {email[2]}\n"
                    f"**Body:** {email[3]}\n\n"
                    "Does this email relate to a meeting, scheduling, or a request for an online discussion? "
                    "If so, proceed with the request as per the instructions provided."
                )
                # Pass the prompt to the agent
                print(f"Generated prompt: {prompt}")  # Debug statement
                try:
                    agent.print_response(prompt)
                    print("Prompt successfully passed to agent.")
                except Exception as e:
                    print(f"Error passing prompt to agent: {e}")
        time.sleep(30)


if __name__ == "__main__":
    process_emails()