# AI-Powered Email Processing Agent

This project is an AI-powered email processing agent designed to automate the handling of unread emails, particularly focusing on meeting requests. Here's a detailed explanation of what the project does:

## Overview

The AI agent continuously monitors an email inbox for unread emails. When it detects a new email, it processes the email to determine if it contains a meeting request. Based on the content of the email and the availability of the requested meeting time, the agent either schedules the meeting or sends a polite decline with alternative time slots.

## Key Features

1. **Fetch Unread Emails**: The agent uses the `FetchUnreadEmail_tool` to fetch unread emails from an IMAP server.
2. **Identify Meeting Requests**: It parses the emails to identify if they contain meeting requests.
3. **Schedule Meetings**: If the requested meeting time is available, it uses the `Zoom_tool` to schedule a Zoom meeting and the `Calcom_tool` to create a booking.
4. **Send Emails**: It uses the `SendEmail_tool` to send confirmation or decline emails based on the availability of the requested meeting time.
5. **Retry Mechanism**: The agent includes a retry mechanism to handle errors in fetching emails.

## Tools Used

### FetchUnreadEmail_tool

- **Purpose**: Fetches unread emails from the specified IMAP server.
- **Functionality**: Connects to the IMAP server, retrieves unread emails, and returns them for processing.

### Zoom_tool

- **Purpose**: Schedules Zoom meetings.
- **Functionality**: Uses Zoom API credentials to create a Zoom meeting and returns the meeting link.

### Calcom_tool

- **Purpose**: Creates bookings and checks availability.
- **Functionality**: Checks if the requested meeting time is available. Declines if the meeting falls on weekends, Japan national holidays, or restricted weekday hours (before 9 AM, between 1 PM and 2 PM, or after 6 PM). Creates a booking if the time is available.

### SendEmail_tool

- **Purpose**: Sends emails to specified recipients.
- **Functionality**: Uses SMTP server credentials to send emails, including meeting confirmations and polite declines.

## How It Works

1. **Setup**: The agent is configured with environment variables for email and tool credentials.
2. **Fetch Emails**: The `fetch_unread_emails_with_retry` function fetches unread emails with a retry mechanism.
3. **Process Emails**: The `process_emails` function processes each email to determine if it contains a meeting request.
4. **Handle Meeting Requests**:
    - If the requested meeting time is not available, it generates an email to politely decline the request with alternative time slots.
    - If the requested meeting time is available, it schedules a Zoom meeting, creates a booking with `Calcom_tool`, and sends a confirmation email.
5. **Email Template**: Uses a predefined email template to ensure professional and polite communication.

## Example Email Template

```plaintext
[相手の名前] 様

お世話になっております。[私の名前] です。

[メールの目的や内容を簡潔に述べる]

[詳細な説明や必要な情報を提供する]

何卒よろしくお願い申し上げます。

[私の名前]
```

## Important Guidelines

- Ignore emails from specific addresses like `noreply@...`.
- Use clear, professional, and polite language in all communications.
- Confirm the proposed time and date with the user if there is any uncertainty.
- If the requested email meeting time falls on a weekend or during restricted weekday hours, it politely denies the request and provides upcoming available time slots.

## Debugging

Enable debug mode by setting `debug_mode=True` in the agent script to print additional debug information to the console.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

This project automates the process of handling meeting requests in emails, making it efficient and ensuring professional communication.
