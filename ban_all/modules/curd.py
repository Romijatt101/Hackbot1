# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import Session
# from ban_all import Base

# class BannedUser(Base):
#     __tablename__ = 'banned_users'
#     id = Column(Integer, primary_key=True)
#     chat_id = Column(String, index=True)
#     user_id = Column(String, index=True)


# def add_ban_record(db_session: Session, chat_id: str, user_id: str):
#     ban_record = BannedUser(chat_id=chat_id, user_id=user_id)
#     db_session.add(ban_record)
#     db_session.commit()

# def get_banned_users(db_session: Session, chat_id: str):
#     return db_session.query(BannedUser.user_id).filter(BannedUser.chat_id == chat_id).all()

# def clear_ban_records_for_chat(db_session: Session, chat_id: str):
#     db_session.query(BannedUser).filter(BannedUser.chat_id == chat_id).delete()
#     db_session.commit()
