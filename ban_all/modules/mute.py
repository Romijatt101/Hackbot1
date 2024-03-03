from sqlalchemy import Column, Integer, Boolean,BigInteger
from ban_all import Base, SESSION, run_in_exc
import threading

class ChatMuteStatus(Base):
    __tablename__ = "chat_mute_status"
    chat_id = Column(BigInteger, primary_key=True, nullable=False)
    is_muted = Column(Boolean, default=False)

    def __init__(self, chat_id, is_muted=False):
        self.chat_id = chat_id
        self.is_muted = is_muted

    def __eq__(self, other):
        return bool(isinstance(other, ChatMuteStatus)
                    and self.chat_id == other.chat_id
                    and self.is_muted == other.is_muted)

ChatMuteStatus.__table__.create(bind=SESSION.get_bind(), checkfirst=True)

CHAT_MUTE_STATUS_INSERTION_LOCK = threading.RLock()

@run_in_exc
def update_chat_mute_status(chat_id, is_muted):
    with CHAT_MUTE_STATUS_INSERTION_LOCK:
        mute_status = ChatMuteStatus(chat_id, is_muted)

        SESSION.merge(mute_status)
        SESSION.commit()

@run_in_exc
def get_chat_mute_status(chat_id):
    mute_status = SESSION.query(ChatMuteStatus).filter(ChatMuteStatus.chat_id == chat_id).first()
    return mute_status.is_muted if mute_status else False
