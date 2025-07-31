from fastapi import APIRouter, HTTPException, Query, Depends, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.gmail_client import GmailClient
from agents.yellow_agent import YellowAgent
from models.email_models import EmailDB, EmailDraftDB
from database import db

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Gmail API"])

# OAuth token validation
async def validate_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        # Extract token from "Bearer <token>" format
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization
        return token
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authorization token")

class EmailDraftRequest(BaseModel):
    draft_content: str

class EmailApprovalRequest(BaseModel):
    approved: bool
    modified_content: Optional[str] = None

# Initialize Yellow Agent
yellow_agent = YellowAgent()

@router.get("/gmail/emails")
async def fetch_user_emails(user_token: str = Query(..., description="OAuth token of the user")):
    """
    Fetch emails from Gmail API using Yellow Agent
    """
    try:
        # Extract user ID from token (simplified - in production, decode JWT properly)
        user_id = "user_" + user_token[-10:]  # Use last 10 chars as user ID
        
        # Use Yellow Agent to fetch emails
        result = await yellow_agent.fetch_user_emails(user_token, user_id)
        
        return {
            "status": "success",
            "message": "Email fetch task queued",
            "task_id": result["task_id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")

@router.get("/gmail/emails/list")
async def list_user_emails(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(20, description="Number of emails to return")
):
    """
    List stored emails for a user
    """
    try:
        cursor = db.emails.find({
            "recipient": {"$regex": user_id, "$options": "i"}
        }).sort("timestamp", -1).limit(limit)
        
        emails = []
        async for email in cursor:
            # Get context if available
            context = await db.email_contexts.find_one({"email_id": email["message_id"]})
            email["context"] = context or {}
            emails.append(email)
        
        return {
            "status": "success",
            "emails": emails,
            "count": len(emails)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list emails: {str(e)}")

@router.get("/gmail/emails/{email_id}")
async def get_email_details(
    email_id: str,
    user_token: str = Query(..., description="OAuth token of the user")
):
    """
    Get detailed email information including context and draft
    """
    try:
        # Get email from database
        email = await db.emails.find_one({"message_id": email_id})
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        # Get context
        context = await db.email_contexts.find_one({"email_id": email_id})
        
        # Get draft if available
        draft = await db.email_drafts.find_one({
            "email_id": email_id,
            "status": {"$in": ["pending", "approved"]}
        })
        
        return {
            "status": "success",
            "email": email,
            "context": context,
            "draft": draft
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get email details: {str(e)}")

@router.post("/gmail/emails/{email_id}/draft")
async def generate_email_draft(
    email_id: str,
    user_token: str = Query(..., description="OAuth token of the user")
):
    """
    Generate AI draft reply for email using Yellow Agent
    """
    try:
        user_id = "user_" + user_token[-10:]
        
        # Create task for Yellow Agent to generate draft
        task_id = await yellow_agent.create_task("generate_draft", {
            "email_id": email_id,
            "user_id": user_id,
            "user_token": user_token
        }, priority=4)
        
        return {
            "status": "success",
            "message": "Draft generation task queued",
            "task_id": task_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate draft: {str(e)}")

@router.get("/gmail/drafts")
async def get_pending_drafts(
    user_id: str = Query(..., description="User ID")
):
    """
    Get pending email drafts for user approval
    """
    try:
        drafts = await yellow_agent.get_email_drafts(user_id)
        
        return {
            "status": "success",
            "drafts": drafts,
            "count": len(drafts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get drafts: {str(e)}")

@router.post("/gmail/drafts/{draft_id}/approve")
async def approve_draft(
    draft_id: str,
    approval: EmailApprovalRequest,
    user_token: str = Query(..., description="OAuth token of the user")
):
    """
    Approve and send email draft
    """
    try:
        if approval.approved:
            # If content was modified, update the draft first
            if approval.modified_content:
                await db.email_drafts.update_one(
                    {"_id": draft_id},
                    {"$set": {"draft_content": approval.modified_content}}
                )
            
            # Use Yellow Agent to send the email
            result = await yellow_agent.approve_draft(draft_id, user_token)
            
            return {
                "status": "success",
                "message": result["message"]
            }
        else:
            # Reject the draft
            await db.email_drafts.update_one(
                {"_id": draft_id},
                {"$set": {"status": "rejected", "rejected_at": datetime.utcnow()}}
            )
            
            return {
                "status": "success",
                "message": "Draft rejected"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process draft approval: {str(e)}")

@router.post("/gmail/emails/{email_id}/reminder")
async def create_email_reminder(
    email_id: str,
    user_token: str = Query(..., description="OAuth token of the user"),
    reminder_hours: int = Query(24, description="Hours until reminder")
):
    """
    Create calendar reminder for email response
    """
    try:
        user_id = "user_" + user_token[-10:]
        
        # Create task for Yellow Agent to create reminder
        task_id = await yellow_agent.create_task("create_reminder", {
            "email_id": email_id,
            "user_id": user_id,
            "reminder_delay_hours": reminder_hours
        }, priority=2)
        
        return {
            "status": "success",
            "message": "Reminder creation task queued",
            "task_id": task_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create reminder: {str(e)}")

@router.get("/gmail/reminders")
async def get_email_reminders(
    user_id: str = Query(..., description="User ID")
):
    """
    Get active email reminders for user
    """
    try:
        cursor = db.email_reminders.find({
            "user_id": user_id,
            "status": "active"
        }).sort("reminder_time", 1)
        
        reminders = []
        async for reminder in cursor:
            # Get associated email
            email = await db.emails.find_one({"message_id": reminder["email_id"]})
            if email:
                reminder["email"] = {
                    "subject": email["subject"],
                    "sender": email["sender"],
                    "timestamp": email["timestamp"]
                }
                reminders.append(reminder)
        
        return {
            "status": "success",
            "reminders": reminders,
            "count": len(reminders)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reminders: {str(e)}")

@router.post("/gmail/reminders/{reminder_id}/complete")
async def complete_reminder(reminder_id: str):
    """
    Mark email reminder as completed
    """
    try:
        result = await db.email_reminders.update_one(
            {"_id": reminder_id},
            {"$set": {"status": "completed", "completed_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Reminder not found")
        
        return {
            "status": "success",
            "message": "Reminder marked as completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete reminder: {str(e)}")

@router.get("/gmail/stats")
async def get_email_stats(
    user_id: str = Query(..., description="User ID")
):
    """
    Get email statistics for user
    """
    try:
        # Count emails by status
        total_emails = await db.emails.count_documents({
            "recipient": {"$regex": user_id, "$options": "i"}
        })
        
        unread_emails = await db.emails.count_documents({
            "recipient": {"$regex": user_id, "$options": "i"},
            "is_read": False
        })
        
        # Count drafts by status
        pending_drafts = await db.email_drafts.count_documents({
            "user_id": user_id,
            "status": "pending"
        })
        
        sent_drafts = await db.email_drafts.count_documents({
            "user_id": user_id,
            "status": "sent"
        })
        
        # Count active reminders
        active_reminders = await db.email_reminders.count_documents({
            "user_id": user_id,
            "status": "active"
        })
        
        # Get priority distribution
        cursor = db.email_contexts.aggregate([
            {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
        ])
        
        priority_distribution = {}
        async for item in cursor:
            priority_distribution[item["_id"]] = item["count"]
        
        return {
            "status": "success",
            "stats": {
                "total_emails": total_emails,
                "unread_emails": unread_emails,
                "pending_drafts": pending_drafts,
                "sent_drafts": sent_drafts,
                "active_reminders": active_reminders,
                "priority_distribution": priority_distribution
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get email stats: {str(e)}")

@router.post("/gmail/sync")
async def sync_emails(
    user_token: str = Query(..., description="OAuth token of the user"),
    max_results: int = Query(50, description="Maximum number of emails to sync")
):
    """
    Manually trigger email synchronization
    """
    try:
        user_id = "user_" + user_token[-10:]
        
        # Create high-priority task for Yellow Agent
        task_id = await yellow_agent.create_task("fetch_emails", {
            "user_token": user_token,
            "user_id": user_id,
            "max_results": max_results
        }, priority=5)
        
        return {
            "status": "success",
            "message": "Email synchronization started",
            "task_id": task_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync emails: {str(e)}")
