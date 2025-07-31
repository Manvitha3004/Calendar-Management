from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from bson import ObjectId
from typing import List
from datetime import datetime, timezone
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import db, connect_to_mongo, close_mongo_connection
from models.schema import EventBase, EventCreate, EventDB, EventUpdate
from utils.time_utils import to_utc, format_datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Calendar Management API", version="1.0.0")

# CORS middleware - Allow frontend origin
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Calendar Management API is running"}

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Using models from schema.py

# Helper function to convert MongoDB document to Event model
def document_to_event(document):
    if document:
        document["_id"] = str(document["_id"])
        return document
    return None


# Async placeholder for meeting prep summary generation
from typing import Any
import asyncio

async def generate_meeting_prep(title: str, start: str, description: str, attendees: Any) -> list:
    await asyncio.sleep(0)  # Simulate async call
    points = [
        f"Main topic: {title} (Scheduled for {start})",
        f"Review meeting description: {description if description else 'No description provided.'}",
        f"Key participants: {', '.join(attendees) if attendees else 'None'}",
        "Prepare questions or discussion points relevant to the agenda."
    ]
    return points

# Routes
@app.get("/api/events", response_model=List[EventDB])
async def get_events():
    events = []
    cursor = db.events.find().sort("start", 1)  # Sort by start time
    async for document in cursor:
        start_val = document["start"]
        end_val = document["end"]
        if isinstance(start_val, str):
            document["start"] = format_datetime(to_utc(datetime.fromisoformat(start_val)))
        else:
            document["start"] = format_datetime(to_utc(start_val))
        if isinstance(end_val, str):
            document["end"] = format_datetime(to_utc(datetime.fromisoformat(end_val)))
        else:
            document["end"] = format_datetime(to_utc(end_val))
        if "_id" in document:
            document["_id"] = str(document["_id"])
        events.append(EventDB(**document))
    return events

@app.get("/api/agenda")
async def get_agenda():
    # Get today's date at midnight in UTC
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Find upcoming events
    cursor = db.events.find({
        "start": {"$gte": today}
    }).sort([("start", 1), ("agendaOrder", 1)])
    
    events = []
    async for document in cursor:
        start_val = document["start"]
        end_val = document["end"]
        if isinstance(start_val, str):
            document["start"] = format_datetime(to_utc(datetime.fromisoformat(start_val)))
        else:
            document["start"] = format_datetime(to_utc(start_val))
        if isinstance(end_val, str):
            document["end"] = format_datetime(to_utc(datetime.fromisoformat(end_val)))
        else:
            document["end"] = format_datetime(to_utc(end_val))
        if "_id" in document:
            document["_id"] = str(document["_id"])
        events.append(EventDB(**document))
    return events

from datetime import datetime, timezone, timedelta

@app.post("/api/events", response_model=EventDB, status_code=201)
async def create_event(event: EventCreate):
    event_dict = event.dict()
    # Ensure dates are timezone-aware and converted to UTC
    event_dict["start"] = format_datetime(to_utc(event_dict["start"]))
    event_dict["end"] = format_datetime(to_utc(event_dict["end"]))
    
    # Add auto-incrementing agenda order
    last_event = await db.events.find_one(sort=[("agendaOrder", -1)])
    event_dict["agendaOrder"] = (last_event.get("agendaOrder", 0) + 1) if last_event else 1
    
    new_event = await db.events.insert_one(event_dict)
    created_event = await db.events.find_one({"_id": new_event.inserted_id})
    return EventDB(**created_event)

@app.put("/api/events/{event_id}", response_model=EventDB)
async def update_event(event_id: str, event: EventUpdate):
    try:
        object_id = ObjectId(event_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    
    event_dict = event.dict(exclude_unset=True)
    updated_event = await db.events.find_one_and_update(
        {"_id": object_id},
        {"$set": event_dict},
        return_document=True
    )
    
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return EventDB(**updated_event)

@app.delete("/api/events/{event_id}")
async def delete_event(event_id: str):
    try:
        object_id = ObjectId(event_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    
    result = await db.events.delete_one({"_id": object_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event deleted"}

from routes.email_assistant import router as email_assistant_router
from routes.gmail_api import router as gmail_router
from routes.agents import router as agents_router

app.include_router(email_assistant_router, prefix="/api")
app.include_router(gmail_router, prefix="/api")
app.include_router(agents_router, prefix="/api")

@app.get("/api/events/{event_id}/prep")
async def get_meeting_prep(event_id: str):
    try:
        object_id = ObjectId(event_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    event = await db.events.find_one({"_id": object_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    summary_points = await generate_meeting_prep(
        event.get("title", ""),
        event.get("start", ""),
        event.get("meetingDescription", ""),
        event.get("attendees", [])
    )
    await db.events.update_one(
        {"_id": object_id},
        {"$set": {"summaryPoints": summary_points}}
    )
    return {
        "title": event.get("title", ""),
        "meetingDescription": event.get("meetingDescription", ""),
        "summaryPoints": summary_points,
        "start": event.get("start", ""),
        "attendees": event.get("attendees", [])
    }

@app.post("/api/events/{event_id}/regenerate-summary")
async def regenerate_summary(event_id: str):
    try:
        object_id = ObjectId(event_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    event = await db.events.find_one({"_id": object_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    summary_points = await generate_meeting_prep(
        event.get("title", ""),
        event.get("start", ""),
        event.get("meetingDescription", ""),
        event.get("attendees", [])
    )
    await db.events.update_one(
        {"_id": object_id},
        {"$set": {"summaryPoints": summary_points}}
    )
    return {
        "summaryPoints": summary_points,
        "message": "Summary regenerated successfully"
    }

@app.put("/api/events/{event_id}/summary")
async def update_summary_points(event_id: str, summary_points: List[str]):
    try:
        object_id = ObjectId(event_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid event ID")
    
    updated_event = await db.events.find_one_and_update(
        {"_id": object_id},
        {"$set": {"summaryPoints": summary_points}},
        return_document=True
    )
    
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Summary points updated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
