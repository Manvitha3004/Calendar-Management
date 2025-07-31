import os
import asyncio
from utils.gemini_api import generate_gemini_summary

async def generate_meeting_summary(event_title, event_date_time, event_description, attendees=None):
    prompt = f"""
You are a smart meeting assistant. Based on the following event information, generate a concise, professional bullet-point summary for meeting preparation. Use simple language suitable for quick review before joining a meeting.

Title: {event_title}
Date & Time: {event_date_time}
Description: {event_description}
Attendees: {', '.join(attendees) if attendees else 'None'}

Output format:
- Bullet point summary of main topics
- Any required pre-reading or actions
- Key stakeholders or participants to keep in mind (if mentioned)
- Questions the attendee should be ready to answer or ask (make these specific to the description)
"""
    try:
        summary = await generate_gemini_summary(prompt)
        if summary:
            return [line for line in summary.split('\n') if line.strip()]
    except Exception as e:
        pass
    # Fallback to template-based summary
    points = []
    points.append(f"• Main topic: {event_title} (Scheduled for {event_date_time})")
    if event_description and event_description.strip():
        points.append(f"• Review meeting description: {event_description.strip()}")
    else:
        points.append("• No specific agenda provided. Be ready for general discussion.")
    if event_description and ('read' in event_description.lower() or 'prepare' in event_description.lower()):
        points.append("• Complete any pre-reading or preparation mentioned in the description.")
    if attendees:
        if isinstance(attendees, list) and attendees:
            names = ', '.join(attendees)
            points.append(f"• Key participants: {names}")
    points.append("• Prepare questions or discussion points relevant to the agenda.")
    return points