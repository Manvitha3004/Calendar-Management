from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from .schema import PyObjectId

class AgentStatus(BaseModel):
    agent_id: str
    agent_type: str  # yellow, orange, super_orange
    agent_name: str
    status: str = "idle"  # idle, processing, completed, error
    current_task: Optional[str] = None
    last_activity: datetime
    processed_items: int = 0
    error_count: int = 0
    performance_metrics: Dict[str, Any] = {}
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AgentStatusDB(AgentStatus):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

class AgentTask(BaseModel):
    task_id: str
    agent_id: str
    task_type: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    priority: int = 1  # 1-5, 5 being highest
    dependencies: List[str] = []  # task_ids this task depends on
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AgentTaskDB(AgentTask):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

class AgentCoordination(BaseModel):
    coordination_id: str
    user_id: str
    workflow_type: str  # email_processing, schedule_optimization, conflict_resolution
    involved_agents: List[str]
    status: str = "active"  # active, completed, failed
    data_flow: List[Dict[str, Any]] = []  # track data passing between agents
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class AgentCoordinationDB(AgentCoordination):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

class ConflictDetection(BaseModel):
    conflict_id: str
    user_id: str
    conflict_type: str  # time_overlap, overbooked, burnout_risk
    affected_events: List[str]  # event IDs
    severity: str = "medium"  # low, medium, high, critical
    detected_at: datetime
    resolution_status: str = "pending"  # pending, resolved, ignored
    suggested_resolution: Optional[Dict[str, Any]] = None
    auto_resolved: bool = False
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ConflictDetectionDB(ConflictDetection):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

class ScheduleOptimization(BaseModel):
    optimization_id: str
    user_id: str
    optimization_type: str  # daily, weekly, monthly
    original_schedule: List[Dict[str, Any]]
    optimized_schedule: List[Dict[str, Any]]
    improvements: List[str]
    efficiency_score: float
    created_at: datetime
    applied: bool = False
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ScheduleOptimizationDB(ScheduleOptimization):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
