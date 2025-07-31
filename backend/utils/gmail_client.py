import base64
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GmailClient:
    def __init__(self, credentials: Credentials):
        self.service = build('gmail', 'v1', credentials=credentials)
    
    @classmethod
    def from_token(cls, access_token: str):
        """Create GmailClient from access token"""
        credentials = Credentials(token=access_token)
        return cls(credentials)
    
    def list_messages(self, query: str = "", max_results: int = 50) -> List[Dict[str, Any]]:
        """List messages based on query"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            return messages
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get full message details"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            return self._parse_message(message)
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def _parse_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message into structured format"""
        headers = message['payload'].get('headers', [])
        
        # Extract headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        recipient = next((h['value'] for h in headers if h['name'] == 'To'), '')
        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Parse date
        timestamp = self._parse_date(date_str)
        
        # Extract body
        body = self._extract_body(message['payload'])
        
        # Extract snippet
        snippet = message.get('snippet', '')
        
        # Extract labels
        labels = message.get('labelIds', [])
        
        return {
            'message_id': message['id'],
            'thread_id': message['threadId'],
            'subject': subject,
            'sender': self._clean_email(sender),
            'recipient': self._clean_email(recipient),
            'body': body,
            'snippet': snippet,
            'timestamp': timestamp,
            'is_read': 'UNREAD' not in labels,
            'labels': labels,
            'attachments': self._extract_attachments(message['payload'])
        }
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data and not body:  # Use HTML if no plain text
                        html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        body = self._html_to_text(html_body)
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def _extract_attachments(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract attachment information"""
        attachments = []
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    attachments.append({
                        'filename': part['filename'],
                        'mimeType': part['mimeType'],
                        'size': part['body'].get('size', 0)
                    })
        
        return attachments
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime"""
        try:
            # This is a simplified parser - you might want to use a more robust solution
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.now(timezone.utc)
    
    def _clean_email(self, email_str: str) -> str:
        """Extract email address from string like 'Name <email@domain.com>'"""
        match = re.search(r'<(.+?)>', email_str)
        if match:
            return match.group(1)
        return email_str
    
    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text (basic implementation)"""
        # Remove HTML tags
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html)
    
    def send_message(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> bool:
        """Send email message"""
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if thread_id:
                message['In-Reply-To'] = thread_id
                message['References'] = thread_id
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_message = {
                'raw': raw_message
            }
            
            if thread_id:
                send_message['threadId'] = thread_id
            
            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False
    
    def get_unread_messages(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """Get unread messages"""
        messages = self.list_messages(query="is:unread", max_results=max_results)
        full_messages = []
        
        for msg in messages:
            full_msg = self.get_message(msg['id'])
            if full_msg:
                full_messages.append(full_msg)
        
        return full_messages
    
    def mark_as_read(self, message_id: str) -> bool:
        """Mark message as read"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False
    
    def get_thread_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a thread"""
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            messages = []
            for message in thread['messages']:
                parsed_msg = self._parse_message(message)
                messages.append(parsed_msg)
            
            return messages
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
