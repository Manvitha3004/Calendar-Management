import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .base_agent import BaseAgent
from utils.gmail_client import GmailClient
from models.email_models import EmailDB, EmailDraftDB, EmailReminderDB, EmailContextDB
from database import db

class YellowAgent(BaseAgent):
    """
    YELLOW AGENT: Email processing and reply generation
    - Fetch emails from Gmail API
    - Read and extract context from emails
    - Draft reply using simple templates (Gemini API for meeting prep)
    - Present drafted reply to the user for approval
    - Set a reminder on Calendar to reply to the email if not responded yet
    """
    
    def __init__(self, agent_id: str = "yellow_agent_a"):
        super().__init__(agent_id, "Email Assistant", "yellow")
        self.gmail_client = None
    
    async def initialize(self):
        """Initialize the Yellow Agent"""
        print(f"Yellow Agent {self.agent_id} initialized")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process different types of tasks"""
        task_type = task["task_type"]
        input_data = task["input_data"]
        
        if task_type == "fetch_emails":
            return await self._fetch_emails(input_data)
        elif task_type == "process_email":
            return await self._process_email(input_data)
        elif task_type == "generate_draft":
            return await self._generate_draft(input_data)
        elif task_type == "create_reminder":
            return await self._create_reminder(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _fetch_emails(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch emails from Gmail API"""
        user_token = input_data.get("user_token")
        user_id = input_data.get("user_id")
        max_results = input_data.get("max_results", 20)
        
        if not user_token:
            raise ValueError("User token is required")
        
        try:
            # Initialize Gmail client with user token
            gmail_client = GmailClient.from_token(user_token)
            
            # Fetch unread emails
            messages = gmail_client.get_unread_messages(max_results)
            
            # Store emails in database
            stored_emails = []
            for message in messages:
                email_data = EmailDB(
                    **message,
                    id=message["message_id"]  # Use Gmail message ID as our ID
                )
                
                # Check if email already exists
                existing = await db.emails.find_one({"message_id": message["message_id"]})
                if not existing:
                    await db.emails.insert_one(email_data.dict())
                    stored_emails.append(email_data.dict())
                    
                    # Create task to process this email
                    await self.create_task("process_email", {
                        "email_id": message["message_id"],
                        "user_id": user_id,
                        "user_token": user_token
                    }, priority=3)
            
            return {
                "fetched_count": len(messages),
                "stored_count": len(stored_emails),
                "emails": stored_emails
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch emails: {str(e)}")
    
    async def _process_email(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email and extract context"""
        email_id = input_data.get("email_id")
        user_id = input_data.get("user_id")
        
        if not email_id:
            raise ValueError("Email ID is required")
        
        try:
            # Get email from database
            email = await db.emails.find_one({"message_id": email_id})
            if not email:
                raise ValueError(f"Email {email_id} not found")
            
            # Extract context using AI
            context = await self._extract_email_context(email)
            
            # Store context in database
            email_context = EmailContextDB(**context, email_id=email_id)
            await db.email_contexts.replace_one(
                {"email_id": email_id},
                email_context.dict(),
                upsert=True
            )
            
            # If email requires a response, create draft generation task
            if context.get("category") in ["meeting", "task", "question"]:
                await self.create_task("generate_draft", {
                    "email_id": email_id,
                    "user_id": user_id,
                    "user_token": input_data.get("user_token")
                }, priority=4)
            
            return {
                "email_id": email_id,
                "context": context,
                "requires_response": context.get("category") in ["meeting", "task", "question"]
            }
            
        except Exception as e:
            raise Exception(f"Failed to process email: {str(e)}")
    
    async def _extract_email_context(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Extract context from email using simple heuristics"""
        try:
            # Simple heuristic-based analysis
            subject = email.get('subject', '').lower()
            body = email.get('body', '').lower()
            
            # Determine sentiment based on keywords
            sentiment = "neutral"
            if any(word in subject + body for word in ['urgent', 'asap', 'immediately', 'critical']):
                sentiment = "negative"
            elif any(word in subject + body for word in ['thank', 'great', 'excellent', 'congratulations']):
                sentiment = "positive"
            
            # Determine priority based on keywords
            priority = "medium"
            if any(word in subject + body for word in ['urgent', 'asap', 'critical', 'emergency']):
                priority = "urgent"
            elif any(word in subject + body for word in ['important', 'priority', 'deadline']):
                priority = "high"
            elif any(word in subject + body for word in ['fyi', 'info', 'update']):
                priority = "low"
            
            # Determine category based on keywords
            category = "information"
            if any(word in subject + body for word in ['meeting', 'call', 'schedule', 'appointment']):
                category = "meeting"
            elif any(word in subject + body for word in ['task', 'todo', 'action', 'complete']):
                category = "task"
            elif any(word in subject + body for word in ['question', '?', 'help', 'clarify']):
                category = "question"
            elif any(word in subject + body for word in ['complaint', 'issue', 'problem', 'error']):
                category = "complaint"
            
            # Extract key points (simple sentence splitting)
            key_points = [email.get('snippet', 'No content available')]
            
            # Basic suggested actions
            suggested_actions = ["Review and respond if necessary"]
            if category == "meeting":
                suggested_actions = ["Check calendar availability", "Confirm meeting details"]
            elif category == "task":
                suggested_actions = ["Review task requirements", "Set completion timeline"]
            elif category == "question":
                suggested_actions = ["Provide requested information", "Answer questions"]
            
            return {
                "sentiment": sentiment,
                "priority": priority,
                "category": category,
                "key_points": key_points,
                "suggested_actions": suggested_actions,
                "extracted_entities": {}
            }
            
        except Exception as e:
            print(f"Error extracting context: {e}")
            # Return basic context on error
            return {
                "sentiment": "neutral",
                "priority": "medium",
                "category": "information",
                "key_points": [email.get('snippet', 'No content available')],
                "suggested_actions": ["Review and respond if necessary"],
                "extracted_entities": {}
            }
    
    async def _generate_draft(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI draft reply for email"""
        email_id = input_data.get("email_id")
        user_id = input_data.get("user_id")
        
        if not email_id:
            raise ValueError("Email ID is required")
        
        try:
            # Get email and context
            email = await db.emails.find_one({"message_id": email_id})
            context = await db.email_contexts.find_one({"email_id": email_id})
            
            if not email:
                raise ValueError(f"Email {email_id} not found")
            
            # Generate draft using AI
            draft_content = await self._generate_ai_draft(email, context)
            
            # Store draft in database
            draft = EmailDraftDB(
                email_id=email_id,
                draft_content=draft_content,
                generated_at=datetime.utcnow(),
                status="pending",
                ai_confidence=0.8,  # Could be calculated based on AI response
                user_id=user_id
            )
            
            await db.email_drafts.insert_one(draft.dict())
            
            # Create reminder task if draft is not approved within 24 hours
            await self.create_task("create_reminder", {
                "email_id": email_id,
                "user_id": user_id,
                "reminder_delay_hours": 24
            }, priority=2)
            
            return {
                "email_id": email_id,
                "draft_id": str(draft.id),
                "draft_content": draft_content,
                "status": "pending_approval"
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate draft: {str(e)}")
    
    async def _generate_ai_draft(self, email: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Generate template-based draft reply"""
        try:
            subject = email.get('subject', 'your email')
            sender = email.get('sender', 'you')
            category = context.get('category', 'general') if context else 'general'
            
            # Generate template-based response based on category
            if category == "meeting":
                return f"Thank you for your email regarding '{subject}'. I have reviewed the meeting details and will check my calendar availability. I'll get back to you shortly with my response."
            elif category == "task":
                return f"Thank you for your email regarding '{subject}'. I have noted the task requirements and will review them carefully. I'll provide an update on the timeline and next steps soon."
            elif category == "question":
                return f"Thank you for your email regarding '{subject}'. I have received your questions and will provide the requested information as soon as possible."
            elif category == "complaint":
                return f"Thank you for bringing this matter to my attention regarding '{subject}'. I understand your concerns and will investigate this issue promptly. I'll follow up with you once I have more information."
            else:
                return f"Thank you for your email regarding '{subject}'. I have received your message and will review it carefully. I'll get back to you soon with a response."
            
        except Exception as e:
            print(f"Error generating template draft: {e}")
            return f"Thank you for your email. I will review this and get back to you soon."
    
    async def _create_reminder(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create calendar reminder for email response"""
        email_id = input_data.get("email_id")
        user_id = input_data.get("user_id")
        reminder_delay_hours = input_data.get("reminder_delay_hours", 24)
        
        if not email_id:
            raise ValueError("Email ID is required")
        
        try:
            # Get email details
            email = await db.emails.find_one({"message_id": email_id})
            if not email:
                raise ValueError(f"Email {email_id} not found")
            
            # Calculate reminder time
            reminder_time = datetime.utcnow() + timedelta(hours=reminder_delay_hours)
            
            # Create reminder
            reminder = EmailReminderDB(
                email_id=email_id,
                user_id=user_id,
                reminder_time=reminder_time,
                status="active",
                created_at=datetime.utcnow()
            )
            
            await db.email_reminders.insert_one(reminder.dict())
            
            # TODO: Create actual calendar event using Google Calendar API
            # This would require integration with the calendar system
            
            return {
                "email_id": email_id,
                "reminder_id": str(reminder.id),
                "reminder_time": reminder_time,
                "status": "created"
            }
            
        except Exception as e:
            raise Exception(f"Failed to create reminder: {str(e)}")
    
    
    async def fetch_user_emails(self, user_token: str, user_id: str) -> Dict[str, Any]:
        """Public method to fetch emails for a user"""
        task_id = await self.create_task("fetch_emails", {
            "user_token": user_token,
            "user_id": user_id,
            "max_results": 20
        }, priority=5)
        
        return {"task_id": task_id, "status": "queued"}
    
    async def get_email_drafts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending email drafts for user approval"""
        cursor = db.email_drafts.find({
            "user_id": user_id,
            "status": "pending"
        }).sort("generated_at", -1)
        
        drafts = []
        async for draft in cursor:
            # Get associated email
            email = await db.emails.find_one({"message_id": draft["email_id"]})
            if email:
                draft["email"] = email
                drafts.append(draft)
        
        return drafts
    
    async def approve_draft(self, draft_id: str, user_token: str) -> Dict[str, Any]:
        """Approve and send email draft"""
        try:
            # Get draft
            draft = await db.email_drafts.find_one({"_id": draft_id})
            if not draft:
                raise ValueError("Draft not found")
            
            # Get original email
            email = await db.emails.find_one({"message_id": draft["email_id"]})
            if not email:
                raise ValueError("Original email not found")
            
            # Send email using Gmail API
            gmail_client = GmailClient.from_token(user_token)
            success = gmail_client.send_message(
                to=email["sender"],
                subject=f"Re: {email['subject']}",
                body=draft["draft_content"],
                thread_id=email["thread_id"]
            )
            
            if success:
                # Update draft status
                await db.email_drafts.update_one(
                    {"_id": draft_id},
                    {"$set": {"status": "sent", "sent_at": datetime.utcnow()}}
                )
                
                # Cancel reminder
                await db.email_reminders.update_many(
                    {"email_id": draft["email_id"]},
                    {"$set": {"status": "completed"}}
                )
                
                return {"status": "sent", "message": "Email sent successfully"}
            else:
                raise Exception("Failed to send email")
                
        except Exception as e:
            await db.email_drafts.update_one(
                {"_id": draft_id},
                {"$set": {"status": "failed", "error": str(e)}}
            )
            raise Exception(f"Failed to send email: {str(e)}")
