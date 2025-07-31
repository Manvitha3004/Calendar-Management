from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models.agent_models import ConflictDetection

class ConflictDetector:
    def __init__(self):
        self.buffer_time = timedelta(minutes=15)  # Default buffer between meetings
        self.max_daily_meetings = 8
        self.max_consecutive_hours = 4
        self.burnout_threshold = 6  # hours per day
    
    def detect_conflicts(self, events: List[Dict[str, Any]], user_id: str) -> List[ConflictDetection]:
        """Detect various types of conflicts in the schedule"""
        conflicts = []
        
        # Sort events by start time
        sorted_events = sorted(events, key=lambda x: x['start'])
        
        # Check for time overlaps
        conflicts.extend(self._detect_time_overlaps(sorted_events, user_id))
        
        # Check for overbooking (too many meetings in a day)
        conflicts.extend(self._detect_overbooking(sorted_events, user_id))
        
        # Check for burnout risk (too many consecutive hours)
        conflicts.extend(self._detect_burnout_risk(sorted_events, user_id))
        
        # Check for insufficient buffer time
        conflicts.extend(self._detect_insufficient_buffer(sorted_events, user_id))
        
        return conflicts
    
    def _detect_time_overlaps(self, events: List[Dict[str, Any]], user_id: str) -> List[ConflictDetection]:
        """Detect overlapping events"""
        conflicts = []
        
        for i in range(len(events) - 1):
            current_event = events[i]
            next_event = events[i + 1]
            
            current_end = current_event['end']
            next_start = next_event['start']
            
            if isinstance(current_end, str):
                current_end = datetime.fromisoformat(current_end.replace('Z', '+00:00'))
            if isinstance(next_start, str):
                next_start = datetime.fromisoformat(next_start.replace('Z', '+00:00'))
            
            if current_end > next_start:
                conflict = ConflictDetection(
                    conflict_id=f"overlap_{current_event['id']}_{next_event['id']}",
                    user_id=user_id,
                    conflict_type="time_overlap",
                    affected_events=[current_event['id'], next_event['id']],
                    severity="high",
                    detected_at=datetime.utcnow(),
                    suggested_resolution={
                        "type": "reschedule",
                        "options": [
                            {
                                "action": "move_second_event",
                                "new_start": current_end + self.buffer_time,
                                "reason": "Move second event to avoid overlap"
                            },
                            {
                                "action": "shorten_first_event",
                                "new_end": next_start - self.buffer_time,
                                "reason": "Shorten first event to avoid overlap"
                            }
                        ]
                    }
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _detect_overbooking(self, events: List[Dict[str, Any]], user_id: str) -> List[ConflictDetection]:
        """Detect days with too many meetings"""
        conflicts = []
        daily_events = {}
        
        for event in events:
            start_time = event['start']
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            date_key = start_time.date()
            if date_key not in daily_events:
                daily_events[date_key] = []
            daily_events[date_key].append(event)
        
        for date, day_events in daily_events.items():
            if len(day_events) > self.max_daily_meetings:
                conflict = ConflictDetection(
                    conflict_id=f"overbook_{date}_{user_id}",
                    user_id=user_id,
                    conflict_type="overbooked",
                    affected_events=[e['id'] for e in day_events],
                    severity="medium",
                    detected_at=datetime.utcnow(),
                    suggested_resolution={
                        "type": "redistribute",
                        "current_count": len(day_events),
                        "recommended_count": self.max_daily_meetings,
                        "suggestion": "Consider moving some meetings to other days"
                    }
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _detect_burnout_risk(self, events: List[Dict[str, Any]], user_id: str) -> List[ConflictDetection]:
        """Detect potential burnout from too many consecutive hours of meetings"""
        conflicts = []
        daily_events = {}
        
        # Group events by day
        for event in events:
            start_time = event['start']
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            date_key = start_time.date()
            if date_key not in daily_events:
                daily_events[date_key] = []
            daily_events[date_key].append(event)
        
        for date, day_events in daily_events.items():
            # Sort events by start time
            day_events.sort(key=lambda x: x['start'])
            
            total_meeting_hours = 0
            consecutive_hours = 0
            max_consecutive = 0
            
            for i, event in enumerate(day_events):
                start_time = event['start']
                end_time = event['end']
                
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                
                duration = (end_time - start_time).total_seconds() / 3600  # hours
                total_meeting_hours += duration
                
                # Check for consecutive meetings
                if i > 0:
                    prev_end = day_events[i-1]['end']
                    if isinstance(prev_end, str):
                        prev_end = datetime.fromisoformat(prev_end.replace('Z', '+00:00'))
                    
                    gap = (start_time - prev_end).total_seconds() / 60  # minutes
                    if gap <= 30:  # Less than 30 minutes gap
                        consecutive_hours += duration
                    else:
                        max_consecutive = max(max_consecutive, consecutive_hours)
                        consecutive_hours = duration
                else:
                    consecutive_hours = duration
            
            max_consecutive = max(max_consecutive, consecutive_hours)
            
            if total_meeting_hours > self.burnout_threshold or max_consecutive > self.max_consecutive_hours:
                severity = "critical" if total_meeting_hours > self.burnout_threshold * 1.5 else "high"
                
                conflict = ConflictDetection(
                    conflict_id=f"burnout_{date}_{user_id}",
                    user_id=user_id,
                    conflict_type="burnout_risk",
                    affected_events=[e['id'] for e in day_events],
                    severity=severity,
                    detected_at=datetime.utcnow(),
                    suggested_resolution={
                        "type": "schedule_breaks",
                        "total_hours": total_meeting_hours,
                        "max_consecutive": max_consecutive,
                        "recommendations": [
                            "Add 15-minute breaks between meetings",
                            "Consider moving some meetings to other days",
                            "Block time for focused work"
                        ]
                    }
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _detect_insufficient_buffer(self, events: List[Dict[str, Any]], user_id: str) -> List[ConflictDetection]:
        """Detect meetings with insufficient buffer time"""
        conflicts = []
        
        for i in range(len(events) - 1):
            current_event = events[i]
            next_event = events[i + 1]
            
            current_end = current_event['end']
            next_start = next_event['start']
            
            if isinstance(current_end, str):
                current_end = datetime.fromisoformat(current_end.replace('Z', '+00:00'))
            if isinstance(next_start, str):
                next_start = datetime.fromisoformat(next_start.replace('Z', '+00:00'))
            
            gap = next_start - current_end
            
            if timedelta(0) < gap < self.buffer_time:
                conflict = ConflictDetection(
                    conflict_id=f"buffer_{current_event['id']}_{next_event['id']}",
                    user_id=user_id,
                    conflict_type="insufficient_buffer",
                    affected_events=[current_event['id'], next_event['id']],
                    severity="low",
                    detected_at=datetime.utcnow(),
                    suggested_resolution={
                        "type": "add_buffer",
                        "current_gap": gap.total_seconds() / 60,  # minutes
                        "recommended_gap": self.buffer_time.total_seconds() / 60,
                        "suggestion": f"Add {self.buffer_time.total_seconds() / 60} minutes buffer between meetings"
                    }
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def suggest_reschedule(self, conflict: ConflictDetection, available_slots: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Suggest reschedule options for a conflict"""
        if conflict.conflict_type == "time_overlap":
            return self._suggest_overlap_resolution(conflict, available_slots)
        elif conflict.conflict_type == "overbooked":
            return self._suggest_redistribution(conflict, available_slots)
        elif conflict.conflict_type == "burnout_risk":
            return self._suggest_burnout_resolution(conflict, available_slots)
        
        return None
    
    def _suggest_overlap_resolution(self, conflict: ConflictDetection, available_slots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest resolution for overlapping events"""
        return {
            "type": "reschedule_options",
            "options": [
                {
                    "event_id": conflict.affected_events[1],
                    "action": "move",
                    "available_slots": available_slots[:3]  # Top 3 suggestions
                }
            ]
        }
    
    def _suggest_redistribution(self, conflict: ConflictDetection, available_slots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest redistribution for overbooked days"""
        return {
            "type": "redistribute_meetings",
            "excess_count": len(conflict.affected_events) - self.max_daily_meetings,
            "available_slots": available_slots
        }
    
    def _suggest_burnout_resolution(self, conflict: ConflictDetection, available_slots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest resolution for burnout risk"""
        return {
            "type": "add_breaks_and_redistribute",
            "recommendations": [
                "Add 15-minute breaks between consecutive meetings",
                "Move some meetings to less busy days",
                "Consider shorter meeting durations"
            ],
            "alternative_slots": available_slots
        }
