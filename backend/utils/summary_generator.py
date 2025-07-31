def generate_meeting_summary(event_title, agenda, participants):
    """
    Generate a meeting summary using template-based approach.
    This is a fallback implementation since OpenAI has been removed.
    """
    try:
        # Create a template-based summary
        summary = f"Meeting: {event_title}\n"
        if agenda:
            summary += f"Agenda: {agenda}\n"
        if participants:
            summary += f"Participants: {participants}\n"
        
        summary += "\nKey Points:\n"
        if agenda:
            # Extract key points from agenda
            points = [point.strip() for point in agenda.split('\n') if point.strip()]
            for i, point in enumerate(points[:5], 1):  # Limit to 5 points
                summary += f"{i}. {point}\n"
        else:
            summary += "- No specific agenda provided\n"
            
        return summary.strip()
    except Exception as e:
        print("Summary generation error:", e)
        return "Summary generation failed."

def generate_meeting_summary_simple(description: str) -> list[str]:
    """
    Generates summary points from meeting description using simple text processing.
    Fallback function when OpenAI is not available.
    """
    if not description:
        return ["No description provided"]
    
    # Split by sentences and newlines
    points = []
    sentences = [s.strip() for s in description.replace('\n', '. ').split('.') if s.strip()]
    
    for sentence in sentences:
        if len(sentence) > 10:  # Only include meaningful sentences
            points.append(f"• {sentence}")
    
    return points if points else ["No key points identified"]

def generate_meeting_prep(event_title, event_date_time, event_description, attendees=None):
    points = []
    # Main topic
    points.append(f"• Main topic: {event_title} (Scheduled for {event_date_time})")
    # Description summary
    if event_description and event_description.strip():
        points.append(f"• Review meeting description: {event_description.strip()}")
    else:
        points.append("• No specific agenda provided. Be ready for general discussion.")
    # Pre-reading/actions
    if 'read' in event_description.lower() or 'prepare' in event_description.lower():
        points.append("• Complete any pre-reading or preparation mentioned in the description.")
    # Stakeholders
    if attendees:
        if isinstance(attendees, list) and attendees:
            names = ', '.join(attendees)
            points.append(f"• Key participants: {names}")
    # Questions
    points.append("• Prepare questions or discussion points relevant to the agenda.")
    return points, prompt
prompt = f"""
You are a smart meeting assistant. Based on the following event information, generate a list of key preparation points that a participant should review before attending the meeting.

Title: {event_title}
Date & Time: {event_date_time}
Description: {event_description}

Output format:
- Bullet point summary of main topics
- Any required pre-reading or actions
- Key stakeholders or participants to keep in mind (if mentioned)
- Questions the attendee should be ready to answer or ask (make these specific to the description)

Only include relevant and concise bullet points. Use simple, professional language suitable for quick review before joining a meeting.
"""