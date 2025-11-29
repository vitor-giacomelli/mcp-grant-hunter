import os
import base64
import logging
from typing import Dict, Any
from datetime import datetime
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic_models import GoogleServicesInput

# Configure logging
logger = logging.getLogger(__name__)


class GoogleServicesManager:
    """Manage Google Services (Gmail, Calendar) with secure token handling"""

    def execute_services(
        self,
        input_data: GoogleServicesInput
    ) -> Dict[str, Any]:
        """Execute Gmail draft creation and Calendar event creation"""

        # DEMO MODE BYPASS
        if os.getenv("DEMO_MODE", "FALSE").upper() == "TRUE":
            logger.info("DEMO_MODE active: Simulating Google Services success.")
            return {
                "gmail_status": "SUCCESS",
                "calendar_status": "SUCCESS",
                "draft_link": (
                    "https://mail.google.com/mail/u/0/#drafts/DEMO123"
                ),
                "event_link": (
                    "https://calendar.google.com/calendar/r/eventedit/DEMO123"
                ),
                "errors": []
            }

        results = {
            "gmail_status": "SKIPPED",
            "calendar_status": "SKIPPED",
            "errors": []
        }

        try:
            # Create credentials from token string
            creds = Credentials(token=input_data.oauth_token)

            # Build services
            gmail_service = build('gmail', 'v1', credentials=creds)
            calendar_service = build('calendar', 'v3', credentials=creds)

            # 1. Create Draft in Gmail
            try:
                draft_link = self._create_draft(gmail_service, input_data)
                results["gmail_status"] = "SUCCESS"
                results["draft_link"] = draft_link
            except HttpError as e:
                if e.resp.status == 401:
                    results["gmail_status"] = "AUTH_ERROR"
                    results["errors"].append(
                        "Gmail: 401 Unauthorized - Token Refresh Required"
                    )
                else:
                    results["gmail_status"] = "FAILED"
                    results["errors"].append(f"Gmail Error: {str(e)}")
            except Exception as e:
                results["gmail_status"] = "FAILED"
                results["errors"].append(f"Gmail Error: {str(e)}")

            # 2. Add Deadline to Calendar
            try:
                event_link = self._add_calendar_event(
                    calendar_service,
                    input_data
                )
                results["calendar_status"] = "SUCCESS"
                results["event_link"] = event_link
            except HttpError as e:
                if e.resp.status == 401:
                    results["calendar_status"] = "AUTH_ERROR"
                    results["errors"].append(
                        "Calendar: 401 Unauthorized - Token Refresh Required"
                    )
                else:
                    results["calendar_status"] = "FAILED"
                    results["errors"].append(f"Calendar Error: {str(e)}")
            except Exception as e:
                results["calendar_status"] = "FAILED"
                results["errors"].append(f"Calendar Error: {str(e)}")

            return results

        except Exception as e:
            logger.error(
                f"Critical error in Google Services Manager: {str(e)}"
            )
            return {
                "status": "CRITICAL_FAILURE",
                "error": str(e)
            }

    def _create_draft(
        self,
        service,
        input_data: GoogleServicesInput
    ) -> str:
        """Create a draft email for the grant"""
        message = MIMEText(
            f"Drafting application for {input_data.grant_title}.\n\n"
            f"Deadline: {input_data.deadline_date}"
        )
        message['to'] = 'me'  # Self-draft
        message['subject'] = f"Grant Application: {input_data.grant_title}"

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft = {'message': {'raw': raw_message}}

        result = service.users().drafts().create(
            userId='me',
            body=draft
        ).execute()
        return f"https://mail.google.com/mail/u/0/#drafts/{result['id']}"

    def _add_calendar_event(
        self,
        service,
        input_data: GoogleServicesInput
    ) -> str:
        """Add grant deadline to calendar"""
        # Parse date
        try:
            deadline_dt = datetime.strptime(
                input_data.deadline_date,
                "%B %d, %Y"
            )
        except ValueError:
            try:
                deadline_dt = datetime.strptime(
                    input_data.deadline_date,
                    "%Y-%m-%d"
                )
            except ValueError:
                # Fallback to today if parse fails
                deadline_dt = datetime.now()

        event = {
            'summary': f'Grant Deadline: {input_data.grant_title}',
            'description': f'Application due for {input_data.grant_title}',
            'start': {
                'date': deadline_dt.strftime('%Y-%m-%d'),
                'timeZone': 'UTC',
            },
            'end': {
                'date': deadline_dt.strftime('%Y-%m-%d'),
                'timeZone': 'UTC',
            },
        }

        result = service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        return result.get('htmlLink', 'Event created')
