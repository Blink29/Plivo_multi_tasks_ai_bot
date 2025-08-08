from typing import Dict, List
import uuid
import time
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        # In-memory storage for sessions (in production, use Redis or database)
        self.sessions: Dict[str, Dict] = {}
        self.session_timeout = 3600  # 1 hour timeout
        
    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'messages': [],
            'query_count': 0,
            'max_queries': 5
        }
        return session_id
    
    def get_session(self, session_id: str) -> Dict:
        """Get session data by ID"""
        if session_id not in self.sessions:
            return None
            
        session = self.sessions[session_id]
        
        # Check if session has expired
        if self._is_session_expired(session):
            del self.sessions[session_id]
            return None
            
        return session
    
    def update_session_activity(self, session_id: str):
        """Update last activity timestamp"""
        if session_id in self.sessions:
            self.sessions[session_id]['last_activity'] = datetime.now()
    
    def add_message_to_session(self, session_id: str, message: str, is_user: bool) -> bool:
        """Add a message to session history"""
        session = self.get_session(session_id)
        if not session:
            return False
            
        message_data = {
            'text': message,
            'isUser': is_user,
            'timestamp': datetime.now().isoformat(),
            'id': int(time.time() * 1000)
        }
        
        session['messages'].append(message_data)
        
        # Increment query count only for user messages
        if is_user:
            session['query_count'] += 1
            
        # Keep only last 10 messages to manage memory
        if len(session['messages']) > 10:
            session['messages'] = session['messages'][-10:]
            
        self.update_session_activity(session_id)
        return True
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        session = self.get_session(session_id)
        if not session:
            return []
        return session['messages']
    
    def can_make_query(self, session_id: str) -> bool:
        """Check if session can make more queries"""
        session = self.get_session(session_id)
        if not session:
            return False
        return session['query_count'] < session['max_queries']
    
    def get_remaining_queries(self, session_id: str) -> int:
        """Get remaining queries for session"""
        session = self.get_session(session_id)
        if not session:
            return 0
        return max(0, session['max_queries'] - session['query_count'])
    
    def _is_session_expired(self, session: Dict) -> bool:
        """Check if session has expired"""
        last_activity = session['last_activity']
        return datetime.now() - last_activity > timedelta(seconds=self.session_timeout)
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if self._is_session_expired(session):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            
        return len(expired_sessions)
