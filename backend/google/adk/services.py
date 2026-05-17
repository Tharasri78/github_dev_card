import uuid

class Session:
    def __init__(self, session_id):
        self.id = session_id

class InMemorySessionService:
    def get_or_create_session(self, username):
        return Session(username)

class InMemoryMemoryService:
    pass
