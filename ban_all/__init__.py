from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from ban_all.config import * # Ensure this imports correctly
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import asyncio
import functools
from pyromod import Client
from typing import Union
from pyrogram.types import Message

# Define BASE before using it
Base = declarative_base()

def start() -> scoped_session:
    engine = create_engine(DB_URL)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))
    
SESSION = start()
bot_client = Client("_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
__client_=[]
file_s = {}
spam_func = {}

max_workers = multiprocessing.cpu_count() * 5
exc_ = ThreadPoolExecutor(max_workers=max_workers)

def run_in_exc(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(exc_, lambda: f(*args, **kwargs))
    return wrapper


def get_text(message: Message) -> Union[None, str]:
    """Extract Text From Commands"""
    text_to_return = message.text
    if message.text is None:
        return None
    if " " not in text_to_return:
        return None
    try:
        return message.text.split(None, 1)[1]
    except IndexError:
        return None