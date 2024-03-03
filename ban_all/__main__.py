import glob
from pathlib import Path
from ban_all.utils import load_plugins
import logging
import asyncio
import importlib
from pyrogram import  idle
from pyrogram.types import *
from ban_all.config import *
from ban_all.modules._utils import *
from ban_all.modules.loggers import *
from ban_all import bot_client,__client_
from ban_all.modules import ALL_MODULES
from pyromod import Client

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# path = "ban_all/modules/*.py"
# files = glob.glob(path)
# print(files)

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("ban_all.modules." + module_name)


from ban_all.modules.session import remove_session, __load_sessions

print("Sir Deployed Ho Gya")
print("Congratulations")
async def start_all_client():
    slist = __load_sessions()
    if slist:
        client_no = 0
        for i in slist:
            client_no += 1
            try:
                client_=Client(
                f"{client_no}_session",
                api_id=API_ID,
                api_hash=API_HASH,
                device_model="iPhone 11 Pro",
                system_version="13.3",
                app_version="8.6",
                session_string=i
            )
                await client_.start()
                client_.myself = await client_.get_me()

            except Exception as e:
                remove_session(i)
                logging.error("Cannot start client {} : {} \nAlso, removed this string from database!".format(client_no, e))
                continue
            __client_.append(client_)
async def run_bot():
    logging.info('Running Bot...')
    await bot_client.start()
    bot_client.myself = await bot_client.get_me()
    logging.info('Info: Bot Started!')
    logging.info('Idling...')
    await idle()
    logging.warning('Exiting Bot....')
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_all_client())
    loop.run_until_complete(run_bot())
