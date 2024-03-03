from sqlalchemy import Column, String
from ban_all import Base, SESSION
import threading

class Session(Base):
    __tablename__ = "sessions"
    session_id = Column(String(255), primary_key=True)

    def __init__(self, session_id):
        self.session_id = session_id

Session.__table__.create(bind=SESSION.get_bind(), checkfirst=True)

SESSION_INSERTION_LOCK = threading.RLock()

ALL_SESSIONS = {}


def add_session(session_id):
    with SESSION_INSERTION_LOCK:
        session_obj = Session(session_id)

        SESSION.merge(session_obj)
        SESSION.commit()
        ALL_SESSIONS.setdefault(session_id, set())


def get_all_sessions():
    return ALL_SESSIONS.keys()


def num_sessions():
    try:
        return SESSION.query(Session).count()
    finally:
        SESSION.close()


def __load_sessions():
    global ALL_SESSIONS
    try:
        sessions = SESSION.query(Session.session_id).all()
        for (session_id,) in sessions:
            ALL_SESSIONS[session_id] = set()
    finally:
        SESSION.close()

def remove_session(session_string):
    SESSION.query(Session).filter(Session.session_id == session_string).delete()


__load_sessions()