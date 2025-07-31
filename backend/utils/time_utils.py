from datetime import datetime, timezone
import pytz

def to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC while preserving the actual time intended by user"""
    if dt.tzinfo is None:
        # If no timezone provided, assume it's in local time
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        local_dt = dt.replace(tzinfo=local_tz)
        return local_dt.astimezone(timezone.utc)
    return dt.astimezone(timezone.utc)

def format_datetime(dt: datetime) -> str:
    """Format datetime for client display"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()