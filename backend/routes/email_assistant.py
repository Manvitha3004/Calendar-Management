from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()

class DraftRequest(BaseModel):
    reply_text: str

@router.get("/emails")
def fetch_emails(user_token: str = Query(..., description="OAuth token of the user")):
    """
    Use Gmail API to fetch unread/recent threads.
    """
    # TODO: Implement Gmail API call using user_token
    return {"message": "fetch_emails endpoint - to be implemented"}

@router.get("/emails/{email_id}")
def read_email(email_id: str, user_token: str = Query(..., description="OAuth token of the user")):
    """
    Get full message using Gmail API.
    """
    # TODO: Implement Gmail API call to get full message using user_token
    return {"message": f"read_email endpoint for email_id {email_id} - to be implemented"}

@router.post("/emails/{email_id}/draft")
def generate_draft(email_id: str, user_token: str = Query(..., description="OAuth token of the user")):
    """
    Call Gemini API with email content to generate draft.
    """
    # TODO: Implement Gemini API call to generate draft reply
    return {"message": f"generate_draft endpoint for email_id {email_id} - to be implemented"}

@router.post("/emails/{email_id}/send")
def send_email_reply(email_id: str, draft_request: DraftRequest, user_token: str = Query(..., description="OAuth token of the user")):
    """
    Use Gmail API to send the draft reply.
    """
    # TODO: Implement Gmail API call to send email reply
    return {"message": f"send_email_reply endpoint for email_id {email_id} - to be implemented"}

@router.post("/emails/{email_id}/reminder")
def create_reminder(email_id: str, user_token: str = Query(..., description="OAuth token of the user")):
    """
    Use Google Calendar API to set reminder for email.
    """
    # TODO: Implement Google Calendar API call to create reminder
    return {"message": f"create_reminder endpoint for email_id {email_id} - to be implemented"}
