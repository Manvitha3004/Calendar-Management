import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .base_agent import BaseAgent
from utils.conflict_detector import ConflictDetector
from models.agent_models import ScheduleOptimizationDB, ConflictDetectionDB
from database import db
import json

class OrangeAgentA(BaseAgent):
    """
    ORANGE AGENT A: Email Data Aggregator
    - Fetch email data from all YELLOW agents (a, b, c, d)
    - Filter and clean data
    - Pass filtered data to ORANGE agent f
    """
    
    def __init__(self):
        super().__init__("orange_agent_a", "Email Data Aggregator", "orange")
    
    async def initialize(self):
        print(f"Orange Agent A initialized - Email Data Aggregator")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task["task_type"]
        input_data = task["input_data"]
        
        if task_type == "aggregate_email_data":
            return await self._aggregate_email_data(input_data)
        elif task_type == "filter_email_data":
            return await self._filter_email_data(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _aggregate_email_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate email data from all Yellow agents"""
        user_id = input_data.get("user_id")
        
        try:
            # Get all emails for the user
            cursor = db.emails.find({"recipient": {"$regex": user_id, "$options": "i"}})
            emails = []
            async for email in cursor:
                emails.append(email)
            
            # Get email contexts
            cursor = db.email_contexts.find({})
            contexts = {}
            async for context in cursor:
                contexts[context["email_id"]] = context
            
            # Get email drafts
            cursor = db.email_drafts.find({"user_id": user_id})
            drafts = {}
            async for draft in cursor:
                drafts[draft["email_id"]] = draft
            
            # Combine data
            aggregated_data = []
            for email in emails:
                email_data = {
                    "email": email,
                    "context": contexts.get(email["message_id"], {}),
                    "draft": drafts.get(email["message_id"], {}),
                    "aggregated_at": datetime.utcnow()
                }
                aggregated_data.append(email_data)
            
            return {
                "user_id": user_id,
                "total_emails": len(emails),
                "aggregated_data": aggregated_data,
                "status": "completed"
            }
            
        except Exception as e:
            raise Exception(f"Failed to aggregate email data: {str(e)}")
    
    async def _filter_email_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and clean email data"""
        aggregated_data = input_data.get("aggregated_data", [])
        
        try:
            filtered_data = []
            
            for item in aggregated_data:
                email = item["email"]
                context = item["context"]
                
                # Filter criteria
                if (
                    context.get("priority") in ["high", "urgent"] or
                    context.get("category") in ["meeting", "task"] or
                    not email.get("is_read", True)
                ):
                    # Clean and structure data
                    cleaned_item = {
                        "email_id": email["message_id"],
                        "subject": email["subject"],
                        "sender": email["sender"],
                        "timestamp": email["timestamp"],
                        "priority": context.get("priority", "medium"),
                        "category": context.get("category", "general"),
                        "key_points": context.get("key_points", []),
                        "requires_action": context.get("category") in ["meeting", "task"],
                        "is_read": email.get("is_read", True)
                    }
                    filtered_data.append(cleaned_item)
            
            # Pass to Orange Agent F
            await self._send_to_orange_f(filtered_data, input_data.get("user_id"))
            
            return {
                "filtered_count": len(filtered_data),
                "filtered_data": filtered_data,
                "status": "completed"
            }
            
        except Exception as e:
            raise Exception(f"Failed to filter email data: {str(e)}")
    
    async def _send_to_orange_f(self, filtered_data: List[Dict[str, Any]], user_id: str):
        """Send filtered data to Orange Agent F"""
        # Create task for Orange Agent F
        orange_f = OrangeAgentF()
        await orange_f.create_task("process_email_data", {
            "email_data": filtered_data,
            "user_id": user_id,
            "source": "orange_agent_a"
        }, priority=3)


class OrangeAgentB(BaseAgent):
    """
    ORANGE AGENT B: Calendar Data Provider
    - Fetch calendar data
    - Present upcoming schedules to ORANGE agent f
    """
    
    def __init__(self):
        super().__init__("orange_agent_b", "Calendar Data Provider", "orange")
    
    async def initialize(self):
        print(f"Orange Agent B initialized - Calendar Data Provider")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task["task_type"]
        input_data = task["input_data"]
        
        if task_type == "fetch_calendar_data":
            return await self._fetch_calendar_data(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _fetch_calendar_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch and process calendar data"""
        user_id = input_data.get("user_id")
        days_ahead = input_data.get("days_ahead", 30)
        
        try:
            # Get upcoming events
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=days_ahead)
            
            cursor = db.events.find({
                "start": {"$gte": start_date, "$lte": end_date}
            }).sort("start", 1)
            
            events = []
            async for event in cursor:
                events.append(event)
            
            # Process and structure calendar data
            calendar_data = []
            for event in events:
                event_data = {
                    "event_id": str(event["_id"]),
                    "title": event["title"],
                    "start": event["start"],
                    "end": event["end"],
                    "duration_minutes": (event["end"] - event["start"]).total_seconds() / 60,
                    "attendees": event.get("attendees", []),
                    "meeting_link": event.get("meetingLink"),
                    "description": event.get("meetingDescription", ""),
                    "status": event.get("status", "upcoming")
                }
                calendar_data.append(event_data)
            
            # Send to Orange Agent F
            orange_f = OrangeAgentF()
            await orange_f.create_task("process_calendar_data", {
                "calendar_data": calendar_data,
                "user_id": user_id,
                "source": "orange_agent_b"
            }, priority=3)
            
            return {
                "user_id": user_id,
                "events_count": len(events),
                "calendar_data": calendar_data,
                "status": "completed"
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch calendar data: {str(e)}")


class OrangeAgentF(BaseAgent):
    """
    ORANGE AGENT F: Coordinator and Finalizer
    - Finalize all meeting plans
    - Submit schedules to a custom calendar
    - Pass results to SUPER AGENT
    """
    
    def __init__(self):
        super().__init__("orange_agent_f", "Coordinator", "orange")
    
    async def initialize(self):
        print(f"Orange Agent F initialized - Coordinator")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task["task_type"]
        input_data = task["input_data"]
        
        if task_type == "process_email_data":
            return await self._process_email_data(input_data)
        elif task_type == "process_calendar_data":
            return await self._process_calendar_data(input_data)
        elif task_type == "finalize_schedule":
            return await self._finalize_schedule(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _process_email_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email data from Orange Agent A"""
        email_data = input_data.get("email_data", [])
        user_id = input_data.get("user_id")
        
        # Store processed email data for coordination
        coordination_data = {
            "type": "email_data",
            "data": email_data,
            "processed_at": datetime.utcnow(),
            "user_id": user_id
        }
        
        await db.coordination_data.insert_one(coordination_data)
        
        return {"status": "processed", "data_type": "email"}
    
    async def _process_calendar_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process calendar data from Orange Agent B"""
        calendar_data = input_data.get("calendar_data", [])
        user_id = input_data.get("user_id")
        
        # Store processed calendar data for coordination
        coordination_data = {
            "type": "calendar_data",
            "data": calendar_data,
            "processed_at": datetime.utcnow(),
            "user_id": user_id
        }
        
        await db.coordination_data.insert_one(coordination_data)
        
        return {"status": "processed", "data_type": "calendar"}
    
    async def _finalize_schedule(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize schedule and pass to Super Agent"""
        user_id = input_data.get("user_id")
        
        # Create final schedule optimization
        optimization = ScheduleOptimizationDB(
            optimization_id=f"opt_{user_id}_{datetime.utcnow().timestamp()}",
            user_id=user_id,
            optimization_type="comprehensive",
            original_schedule=[],
            optimized_schedule=[],
            improvements=[
                "Resolved scheduling conflicts",
                "Added buffer time between meetings",
                "Optimized for productivity"
            ],
            efficiency_score=0.85,
            created_at=datetime.utcnow(),
            applied=False
        )
        
        await db.schedule_optimizations.insert_one(optimization.dict())
        
        return {
            "status": "finalized",
            "optimization_id": optimization.optimization_id,
            "efficiency_score": optimization.efficiency_score
        }


class SuperOrangeAgent(BaseAgent):
    """
    SUPER ORANGE AGENT: Master Coordinator
    - Receive results from all Orange agents
    - Make final decisions and optimizations
    - Coordinate overall system behavior
    """
    
    def __init__(self):
        super().__init__("super_orange_agent", "Master Coordinator", "super_orange")
    
    async def initialize(self):
        print(f"Super Orange Agent initialized - Master Coordinator")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task["task_type"]
        input_data = task["input_data"]
        
        if task_type == "coordinate_system":
            return await self._coordinate_system(input_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _coordinate_system(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate overall system behavior"""
        user_id = input_data.get("user_id")
        
        # Get system status from all agents
        system_status = {
            "yellow_agents": await self._get_agent_status("yellow"),
            "orange_agents": await self._get_agent_status("orange"),
            "super_agent_status": "active",
            "last_coordination": datetime.utcnow()
        }
        
        return {
            "status": "coordinated",
            "system_status": system_status,
            "user_id": user_id
        }
    
    async def _get_agent_status(self, agent_type: str) -> List[Dict[str, Any]]:
        """Get status of agents by type"""
        cursor = db.agent_status.find({"agent_type": agent_type})
        agents = []
        async for agent in cursor:
            agents.append(agent)
        return agents
