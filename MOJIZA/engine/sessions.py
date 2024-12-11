# MOJIZA/engine/sessions.py

import uuid

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self):
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {}
        return session_id
    
    def get_session(self, session_id):
        return self.sessions.get(session_id, {})
    
    def set_session_data(self, session_id, key, value):
        if session_id in self.sessions:
            self.sessions[session_id][key] = value
    
    def get_session_data(self, session_id, key):
        return self.sessions.get(session_id, {}).get(key, None)

session_manager = SessionManager()
