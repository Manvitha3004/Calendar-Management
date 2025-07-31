from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from agents.yellow_agent import YellowAgent
from agents.orange_agents import OrangeAgentA, OrangeAgentB, OrangeAgentF, SuperOrangeAgent
from models.agent_models import AgentStatus, AgentTask, AgentCoordination
from database import db

router = APIRouter()

class AgentTaskRequest(BaseModel):
    task_type: str
    input_data: Dict[str, Any]
    priority: int = 1

class CoordinationRequest(BaseModel):
    workflow_type: str
    user_id: str
    parameters: Dict[str, Any] = {}

# Initialize agents
yellow_agent = YellowAgent()
orange_agent_a = OrangeAgentA()
orange_agent_b = OrangeAgentB()
orange_agent_f = OrangeAgentF()
super_orange_agent = SuperOrangeAgent()

@router.get("/agents/status")
async def get_all_agents_status():
    """
    Get status of all agents in the system
    """
    try:
        cursor = db.agent_status.find({}).sort("last_activity", -1)
        agents = []
        async for agent in cursor:
            agents.append(agent)
        
        # Group by agent type
        agent_groups = {
            "yellow": [a for a in agents if a["agent_type"] == "yellow"],
            "orange": [a for a in agents if a["agent_type"] == "orange"],
            "super_orange": [a for a in agents if a["agent_type"] == "super_orange"]
        }
        
        return {
            "status": "success",
            "agents": agent_groups,
            "total_agents": len(agents),
            "active_agents": len([a for a in agents if a["status"] in ["processing", "idle"]])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")

@router.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """
    Get status of a specific agent
    """
    try:
        agent = await db.agent_status.find_one({"agent_id": agent_id})
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get recent tasks
        cursor = db.agent_tasks.find({
            "agent_id": agent_id
        }).sort("created_at", -1).limit(10)
        
        recent_tasks = []
        async for task in cursor:
            recent_tasks.append(task)
        
        return {
            "status": "success",
            "agent": agent,
            "recent_tasks": recent_tasks
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")

@router.get("/agents/tasks")
async def get_all_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    limit: int = Query(50, description="Number of tasks to return")
):
    """
    Get tasks across all agents
    """
    try:
        query = {}
        if status:
            query["status"] = status
        
        cursor = db.agent_tasks.find(query).sort("created_at", -1).limit(limit)
        
        tasks = []
        async for task in cursor:
            # Get agent info
            agent = await db.agent_status.find_one({"agent_id": task["agent_id"]})
            if agent and (not agent_type or agent["agent_type"] == agent_type):
                task["agent_info"] = {
                    "agent_name": agent["agent_name"],
                    "agent_type": agent["agent_type"]
                }
                tasks.append(task)
        
        return {
            "status": "success",
            "tasks": tasks,
            "count": len(tasks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")

@router.post("/agents/{agent_id}/tasks")
async def create_agent_task(agent_id: str, task_request: AgentTaskRequest):
    """
    Create a new task for a specific agent
    """
    try:
        # Get the appropriate agent instance
        agent = None
        if agent_id == "yellow_agent_a":
            agent = yellow_agent
        elif agent_id == "orange_agent_a":
            agent = orange_agent_a
        elif agent_id == "orange_agent_b":
            agent = orange_agent_b
        elif agent_id == "orange_agent_f":
            agent = orange_agent_f
        elif agent_id == "super_orange_agent":
            agent = super_orange_agent
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Create task
        task_id = await agent.create_task(
            task_request.task_type,
            task_request.input_data,
            task_request.priority
        )
        
        return {
            "status": "success",
            "message": "Task created successfully",
            "task_id": task_id,
            "agent_id": agent_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

@router.get("/agents/tasks/{task_id}")
async def get_task_details(task_id: str):
    """
    Get details of a specific task
    """
    try:
        task = await db.agent_tasks.find_one({"task_id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get agent info
        agent = await db.agent_status.find_one({"agent_id": task["agent_id"]})
        if agent:
            task["agent_info"] = {
                "agent_name": agent["agent_name"],
                "agent_type": agent["agent_type"],
                "status": agent["status"]
            }
        
        return {
            "status": "success",
            "task": task
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task details: {str(e)}")

@router.post("/agents/coordinate")
async def coordinate_workflow(coordination: CoordinationRequest):
    """
    Coordinate a multi-agent workflow
    """
    try:
        workflow_type = coordination.workflow_type
        user_id = coordination.user_id
        parameters = coordination.parameters
        
        # Create coordination record
        coordination_id = f"coord_{user_id}_{datetime.utcnow().timestamp()}"
        
        coordination_record = {
            "coordination_id": coordination_id,
            "user_id": user_id,
            "workflow_type": workflow_type,
            "involved_agents": [],
            "status": "active",
            "data_flow": [],
            "created_at": datetime.utcnow(),
            "parameters": parameters
        }
        
        if workflow_type == "email_processing":
            # Email processing workflow
            coordination_record["involved_agents"] = ["yellow_agent_a", "orange_agent_a", "orange_agent_f"]
            
            # Start with Yellow Agent fetching emails
            await yellow_agent.create_task("fetch_emails", {
                "user_token": parameters.get("user_token"),
                "user_id": user_id,
                "max_results": parameters.get("max_results", 20)
            }, priority=5)
            
            # Queue Orange Agent A to aggregate data
            await orange_agent_a.create_task("aggregate_email_data", {
                "user_id": user_id
            }, priority=4)
            
        elif workflow_type == "schedule_optimization":
            # Schedule optimization workflow
            coordination_record["involved_agents"] = ["orange_agent_b", "orange_agent_f", "super_orange_agent"]
            
            # Start with Orange Agent B fetching calendar data
            await orange_agent_b.create_task("fetch_calendar_data", {
                "user_id": user_id,
                "days_ahead": parameters.get("days_ahead", 30)
            }, priority=4)
            
        elif workflow_type == "conflict_resolution":
            # Conflict resolution workflow
            coordination_record["involved_agents"] = ["orange_agent_b", "orange_agent_f"]
            
            # Start conflict detection process
            await orange_agent_b.create_task("fetch_calendar_data", {
                "user_id": user_id,
                "days_ahead": 7
            }, priority=5)
            
        else:
            raise HTTPException(status_code=400, detail="Unknown workflow type")
        
        # Store coordination record
        await db.agent_coordination.insert_one(coordination_record)
        
        return {
            "status": "success",
            "message": f"{workflow_type} workflow initiated",
            "coordination_id": coordination_id,
            "involved_agents": coordination_record["involved_agents"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to coordinate workflow: {str(e)}")

@router.get("/agents/coordination/{coordination_id}")
async def get_coordination_status(coordination_id: str):
    """
    Get status of a coordination workflow
    """
    try:
        coordination = await db.agent_coordination.find_one({"coordination_id": coordination_id})
        if not coordination:
            raise HTTPException(status_code=404, detail="Coordination not found")
        
        # Get status of involved agents
        agent_statuses = []
        for agent_id in coordination["involved_agents"]:
            agent_status = await db.agent_status.find_one({"agent_id": agent_id})
            if agent_status:
                agent_statuses.append(agent_status)
        
        # Get related tasks
        cursor = db.agent_tasks.find({
            "agent_id": {"$in": coordination["involved_agents"]},
            "created_at": {"$gte": coordination["created_at"]}
        }).sort("created_at", -1)
        
        related_tasks = []
        async for task in cursor:
            related_tasks.append(task)
        
        return {
            "status": "success",
            "coordination": coordination,
            "agent_statuses": agent_statuses,
            "related_tasks": related_tasks
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get coordination status: {str(e)}")

@router.get("/agents/metrics")
async def get_agent_metrics():
    """
    Get performance metrics for all agents
    """
    try:
        # Get task completion stats
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "agent_id": "$agent_id",
                        "status": "$status"
                    },
                    "count": {"$sum": 1}
                }
            }
        ]
        
        cursor = db.agent_tasks.aggregate(pipeline)
        task_stats = {}
        async for stat in cursor:
            agent_id = stat["_id"]["agent_id"]
            status = stat["_id"]["status"]
            count = stat["count"]
            
            if agent_id not in task_stats:
                task_stats[agent_id] = {}
            task_stats[agent_id][status] = count
        
        # Get agent performance metrics
        cursor = db.agent_status.find({})
        agent_metrics = []
        async for agent in cursor:
            agent_id = agent["agent_id"]
            stats = task_stats.get(agent_id, {})
            
            total_tasks = sum(stats.values())
            completed_tasks = stats.get("completed", 0)
            failed_tasks = stats.get("failed", 0)
            
            success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            metrics = {
                "agent_id": agent_id,
                "agent_name": agent["agent_name"],
                "agent_type": agent["agent_type"],
                "status": agent["status"],
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": round(success_rate, 2),
                "last_activity": agent["last_activity"]
            }
            agent_metrics.append(metrics)
        
        return {
            "status": "success",
            "metrics": agent_metrics,
            "summary": {
                "total_agents": len(agent_metrics),
                "active_agents": len([m for m in agent_metrics if m["status"] in ["processing", "idle"]]),
                "total_tasks": sum(m["total_tasks"] for m in agent_metrics),
                "overall_success_rate": round(
                    sum(m["completed_tasks"] for m in agent_metrics) / 
                    max(sum(m["total_tasks"] for m in agent_metrics), 1) * 100, 2
                )
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent metrics: {str(e)}")

@router.post("/agents/start")
async def start_all_agents():
    """
    Start all agents (for development/testing)
    """
    try:
        # This would typically be handled by a process manager in production
        # For now, just update their status to indicate they should be running
        
        agents = [
            ("yellow_agent_a", "Email Assistant", "yellow"),
            ("orange_agent_a", "Email Data Aggregator", "orange"),
            ("orange_agent_b", "Calendar Data Provider", "orange"),
            ("orange_agent_f", "Coordinator", "orange"),
            ("super_orange_agent", "Master Coordinator", "super_orange")
        ]
        
        started_agents = []
        for agent_id, agent_name, agent_type in agents:
            await db.agent_status.update_one(
                {"agent_id": agent_id},
                {
                    "$set": {
                        "agent_id": agent_id,
                        "agent_name": agent_name,
                        "agent_type": agent_type,
                        "status": "idle",
                        "last_activity": datetime.utcnow(),
                        "processed_items": 0,
                        "error_count": 0
                    }
                },
                upsert=True
            )
            started_agents.append(agent_id)
        
        return {
            "status": "success",
            "message": "All agents started",
            "started_agents": started_agents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agents: {str(e)}")

@router.post("/agents/stop")
async def stop_all_agents():
    """
    Stop all agents
    """
    try:
        result = await db.agent_status.update_many(
            {},
            {"$set": {"status": "stopped", "last_activity": datetime.utcnow()}}
        )
        
        return {
            "status": "success",
            "message": f"Stopped {result.modified_count} agents"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop agents: {str(e)}")
