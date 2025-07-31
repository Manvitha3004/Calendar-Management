from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio
import uuid
from models.agent_models import AgentStatus, AgentTask
from database import db

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_name: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.status = "idle"
        self.current_task = None
        self.processed_items = 0
        self.error_count = 0
        self.performance_metrics = {}
        self.last_activity = datetime.utcnow()
    
    async def update_status(self, status: str, current_task: Optional[str] = None):
        """Update agent status in database"""
        self.status = status
        self.current_task = current_task
        self.last_activity = datetime.utcnow()
        
        agent_status = AgentStatus(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            agent_name=self.agent_name,
            status=status,
            current_task=current_task,
            last_activity=self.last_activity,
            processed_items=self.processed_items,
            error_count=self.error_count,
            performance_metrics=self.performance_metrics
        )
        
        await db.agent_status.replace_one(
            {"agent_id": self.agent_id},
            agent_status.dict(),
            upsert=True
        )
    
    async def create_task(self, task_type: str, input_data: Dict[str, Any], priority: int = 1) -> str:
        """Create a new task for this agent"""
        task_id = str(uuid.uuid4())
        
        task = AgentTask(
            task_id=task_id,
            agent_id=self.agent_id,
            task_type=task_type,
            input_data=input_data,
            status="pending",
            created_at=datetime.utcnow(),
            priority=priority
        )
        
        await db.agent_tasks.insert_one(task.dict())
        return task_id
    
    async def update_task(self, task_id: str, status: str, output_data: Optional[Dict[str, Any]] = None, error_message: Optional[str] = None):
        """Update task status and results"""
        update_data = {
            "status": status,
            "last_updated": datetime.utcnow()
        }
        
        if status == "processing" and not await db.agent_tasks.find_one({"task_id": task_id, "started_at": {"$exists": True}}):
            update_data["started_at"] = datetime.utcnow()
        elif status in ["completed", "failed"]:
            update_data["completed_at"] = datetime.utcnow()
        
        if output_data:
            update_data["output_data"] = output_data
        if error_message:
            update_data["error_message"] = error_message
        
        await db.agent_tasks.update_one(
            {"task_id": task_id},
            {"$set": update_data}
        )
    
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get pending tasks for this agent"""
        cursor = db.agent_tasks.find({
            "agent_id": self.agent_id,
            "status": "pending"
        }).sort("priority", -1).sort("created_at", 1)
        
        tasks = []
        async for task in cursor:
            tasks.append(task)
        return tasks
    
    async def process_tasks(self):
        """Main task processing loop"""
        await self.update_status("processing")
        
        try:
            tasks = await self.get_pending_tasks()
            
            for task in tasks:
                try:
                    await self.update_task(task["task_id"], "processing")
                    self.current_task = task["task_type"]
                    
                    # Process the task
                    result = await self.process_task(task)
                    
                    await self.update_task(task["task_id"], "completed", result)
                    self.processed_items += 1
                    
                except Exception as e:
                    await self.update_task(task["task_id"], "failed", error_message=str(e))
                    self.error_count += 1
                    print(f"Error processing task {task['task_id']}: {e}")
            
            await self.update_status("idle")
            
        except Exception as e:
            await self.update_status("error", f"Task processing error: {str(e)}")
            print(f"Agent {self.agent_id} error: {e}")
    
    @abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a specific task - to be implemented by subclasses"""
        pass
    
    async def start(self):
        """Start the agent"""
        await self.update_status("starting")
        await self.initialize()
        await self.update_status("idle")
        
        # Start task processing loop
        while True:
            try:
                await self.process_tasks()
                await asyncio.sleep(5)  # Check for new tasks every 5 seconds
            except Exception as e:
                print(f"Agent {self.agent_id} loop error: {e}")
                await asyncio.sleep(10)  # Wait longer on error
    
    @abstractmethod
    async def initialize(self):
        """Initialize agent - to be implemented by subclasses"""
        pass
    
    async def stop(self):
        """Stop the agent"""
        await self.update_status("stopped")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "status": self.status,
            "processed_items": self.processed_items,
            "error_count": self.error_count,
            "success_rate": (self.processed_items / (self.processed_items + self.error_count)) * 100 if (self.processed_items + self.error_count) > 0 else 0,
            "last_activity": self.last_activity,
            "performance_metrics": self.performance_metrics
        }
