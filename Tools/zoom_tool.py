import os
import time
import requests
from typing import Optional
from dotenv import load_dotenv
from phi.utils.log import logger
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.zoom import ZoomTool

load_dotenv()

# Get environment variables
Zoom_ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
Zoom_CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
Zoom_CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")


class CustomZoomTool(ZoomTool):
    def __init__(
        self,
        account_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        name: str = "zoom_tool",
    ):
        super().__init__(
            account_id=account_id,
            client_id=client_id,
            client_secret=client_secret,
            name=name
        )
        self.token_url = "https://zoom.us/oauth/token"
        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self) -> str:
        """
        Obtain or refresh the access token for Zoom API.
        Returns:
            A string containing the access token or an empty string if token retrieval fails.
        """
        if self.access_token and time.time() < self.token_expires_at:
            return str(self.access_token)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "account_credentials", "account_id": self.account_id}

        try:
            response = requests.post(
                self.token_url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret),
            )
            response.raise_for_status()

            token_info = response.json()
            self.access_token = token_info["access_token"]
            expires_in = token_info["expires_in"]
            self.token_expires_at = time.time() + expires_in - 60

            self._set_parent_token(str(self.access_token))
            return str(self.access_token)
        except requests.RequestException as e:
            logger.error(f"Error fetching access token: {e}")
            return ""

    def _set_parent_token(self, token: str) -> None:
        """Helper method to set the token in the parent ZoomTool class"""
        if token:
            self._ZoomTool__access_token = token


zoom_tools = CustomZoomTool(
    account_id=Zoom_ACCOUNT_ID,
    client_id=Zoom_CLIENT_ID,
    client_secret=Zoom_CLIENT_SECRET,
)

agent = Agent(
    name="Zoom Meeting Manager",
    agent_id="zoom-meeting-manager",
    model=Groq(id="mixtral-8x7b-32768"),  
    tools=[zoom_tools],
    markdown=True,
    # debug_mode=True,
    show_tool_calls=True,
    instructions=[
        "You are an expert at managing Zoom meetings using the Zoom API.",
        "You can:",
        "1. Schedule new meetings (schedule_meeting)",
        "2. Get meeting details (get_meeting)",
        "3. List all meetings (list_meetings)",
        "4. Get upcoming meetings (get_upcoming_meetings)",
        "5. Delete meetings (delete_meeting)",
        "6. Get meeting recordings (get_meeting_recordings)",
        "",
        "For recordings, you can:",
        "- Retrieve recordings for any past meeting using the meeting ID",
        "- Include download tokens if needed",
        "- Get recording details like duration, size, download link and file types",
        "",
        "Guidelines:",
        "- Use ISO 8601 format for dates (e.g., '2024-12-28T10:00:00Z')",
        "- Ensure meeting times are in the future",
        "- Provide meeting details after scheduling (ID, URL, time)",
        "- Handle errors gracefully",
        "- Confirm successful operations",
    ],
)

#Example
# agent.print_response("Schedule a meeting titled 'Team Sync' 8th december at 2 PM UTC for 45 minutes")
# agent.print_response("delete all meeting titled 'Team Sync'")
# agent.print_response("List all my scheduled meetings")
