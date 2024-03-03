import asyncio
import contextlib
import csv
import glob
import logging
import os
import traceback
import aiofiles
import numpy as np
from pyromod import Client
from pyrogram.errors import FloodWait, PeerFlood, UserAlreadyParticipant
from pyrogram.errors.exceptions import UserPrivacyRestricted,UsernameInvalid,SlowmodeWait
from pyrogram.types import Message, User
import numpy as np
from typing import Union
from ban_all import file_s


def digit_wrap(o):
    try:
        return int(o)
    except ValueError:
        return str(o)

async def send_messages_to_user_ids(client, user_ids, message_text):
    success_count = 0
    for user_id in user_ids:
        try:
            await client.send_message(user_id, message_text)
            success_count += 1
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
            continue
        except PeerFlood:
            await asyncio.sleep(5)
            continue
        except UsernameInvalid:
            continue
        except Exception:
            continue
    return success_count


def distribute_user_list_for_clients(user_list: list, num_clients: int) -> list:
    return list(np.array_split(user_list, num_clients))


async def distribute_and_add_users(
    clients: list, user_list: list, target, msg: Message = None
):
    lists__ = distribute_user_list_for_clients(user_list, len(clients))
    if len(clients) == 1:
        return await add_chunks_of_users(clients[0], user_list, target, msg)
    tasks = [
        add_chunks_of_users(client, lists__[i], target, msg)
        for i, client in enumerate(clients)
    ]
    return await asyncio.gather(*tasks)

async def distribute_and_send_messages(
    clients: list, user_ids: list, message_text: str
):
    total_messages_sent = 0  # Counter to keep track of total messages sent

    async def send_messages(client, user_ids, message_text):
        nonlocal total_messages_sent
        messages_sent = await send_messages_to_user_ids(client, user_ids, message_text)
        total_messages_sent += messages_sent

    lists__ = distribute_user_list_for_clients(user_ids, len(clients))

    if len(clients) == 1:
        await send_messages(clients[0], user_ids, message_text)
    else:
        tasks = [
            send_messages(client, lists__[i], message_text)
            for i, client in enumerate(clients)
        ]
        await asyncio.gather(*tasks)

    return total_messages_sent


import random


async def scrap_users(client: Client, chat_id, alg, alww, alwm):
    if isinstance(client, list):
        client = random.choice(client)
    with contextlib.suppress(Exception):
        chat_id = (await client.join_chat(chat_id)).id
    with open(f"users_{chat_id}.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow(
            [
                "first_name",
                "last_name",
                "username (if any)",
                "id",
                "is_bot",
                "last seen (status)",
            ]
        )
        async for user in client.get_chat_members(chat_id):
            if not user.user or not user.user.id or not user.user.status:
                continue
            if alg and user.user.status.LONG_AGO:
                logging.info(f"Ignoring : {user.user.id} - LongTimeAGO")
                continue
            if alww and user.user.status.WITHIN_WEEK:
                logging.info(f"Ignoring : {user.user.id} - WeekSAGO")
                continue
            if alwm and user.user.status.WITHIN_MONTH:
                logging.info(f"Ignorning : {user.user.id} - Months Ago")
                continue
            logging.info(f"Scapping User : {user.user.id}")
            _user: User = user.user
            writer.writerow(
                [
                    _user.first_name,
                    (_user.last_name or "Nil"),
                    (_user.username or "Nil"),
                    int(_user.id),
                    (_user.is_bot or "False"),
                    (str(_user.status) or "Nil"),
                ]
            )
    return f"users_{chat_id}.csv"


def load_from_csv_and_fetch_user_id_list(file_path: str, use_m=False) -> list:
    user_list = []
    with open(file_path, "r", encoding="UTF-8") as f:
        reader = csv.reader(f, delimiter=",", lineterminator="\n")
        for i in reader:
            if use_m:
                if i[2] and i[2] != "username (if any)":
                    user_list.append(i[2])
            else:
                user = i[3]
                if user and user.isdigit():
                    user_list.append(int(user))
    return user_list


from pyrogram.raw import types
from pyrogram.raw.functions.channels import InviteToChannel

async def spam_M(entity, m: Message, no_of_times,Session_list):
    all_spam_funcs = []
    for ic in Session_list:
        all_spam_funcs.extend(spam_c(entity, ic, m) for _ in range(no_of_times))
    await asyncio.gather(*all_spam_funcs)

async def spam_c(entity, c, to_spam):
    try:
        await custom_copy(to_spam,entity, custom_client=c)
    except (FloodWait, SlowmodeWait) as e:
        logging.info(f"['{e.NAME}'] - ('{e.MESSAGE}') - <|'{e.ID}'|> [|'{e.value + 3}'|]")
        await asyncio.sleep(e.value + 3)
    except Exception as e:
        logging.error(e)

async def custom_copy(
        msg : Message,
        chat_id: Union[int, str],
        custom_client: Union[None, Client] = None,
        *args, **kwargs
    ):
        client_ = custom_client
        if msg.text:
            return await client_.send_message(chat_id, text=msg.text, *args, **kwargs)
        elif msg.media:
            if msg.sticker:
                file_id = msg.sticker.file_id
                return await client_.send_sticker(chat_id, sticker=file_id, *args, **kwargs)
            else:
                caption = msg.caption
                if msg.file_id and msg.file_id in file_s:
                    file_ = file_s[msg.file_id]
                    try:
                        await client_.send_cached_media(chat_id, msg.file_id, *args, **kwargs)
                    except Exception as e:
                        logging.error(e)
                        if os.path.exists(file_):
                            try:
                                return await client_.send_file(chat_id, file_, *args, **kwargs)                        
                            except Exception as e:
                                file_s.pop(msg.file_id)
                file_ = await msg.download()
                await client_.send_file(chat_id, file_, caption=caption, *args, **kwargs)
                if msg.file_id:
                    file_s[msg.file_id] = file_
        
async def add_user(client: Client, _user_id, _peer):
    if _user_id:
        return await client.add_chat_members(_peer, [digit_wrap(_user_id)])

def walk_dir(path):
    path = f"{path}*.session"
    return list(glob.iglob(path))


async def log(_text: str, client, msg=None):
    first_ = f"[{client.myself.first_name}_{client.myself.id}]: "
    to_log = first_ + _text
    logging.info(to_log)
    if msg and isinstance(msg, Message):
        with contextlib.suppress(Exception):
            await msg.edit(to_log)


async def write_file(content, file_name):
    if os.path.exists(file_name):
        os.remove(file_name)
    async with aiofiles.open(file_name, "w") as f:
        await f.write(content)
    return file_name


async def add_chunks_of_users(
    client: Client, user_list: list, target, msg: Message = None
):
    with contextlib.suppress(Exception):
        target = (await client.join_chat(target)).id
        print(target,type(target))
    try:
        peer_chat = await client.resolve_peer(target)
        print(peer_chat.type(peer_chat),target)
    except Exception:
        return await log("Target chat not found - invalid peer", client, msg)
    msg = await log("Adding users...", client, msg)
    error_s = f"Errors Raised in {client.myself.first_name}_{client.myself.id}: \n\n"
    added = 0
    failed = 0
    privacy_restricted = 0
    for u_chunk in user_list:
        __user_id = str(u_chunk) if isinstance(u_chunk, str) else int(u_chunk)
        print(__user_id,type(__user_id))
        try:
            await add_user(client, __user_id, peer_chat)
        except UserPrivacyRestricted:
            privacy_restricted += 1
            await log(
                f"User {__user_id} has enabled privacy mode, so failed to add him!",
                client,
                msg,
            )
            continue
        except FloodWait as e:
            await asyncio.sleep(e.value + 5)
            continue
        except PeerFlood:
            await asyncio.sleep(5)
            continue
        except UserAlreadyParticipant:
            await log(
                f"User <code>{__user_id}</code> is already an participant of the chat"
            )
            continue
        except Exception as e:
            error_s += f"{__user_id}: {traceback.format_exc()} \n\n"
            failed += 1
            await log(
                f"Failed to add user - {__user_id} to {target} \nError : {e}",
                client,
                msg,
            )
            continue
        added += 1
        await asyncio.sleep(7)
        await log(f"Added user - {__user_id} to {target}", client, msg)
    if error_s:
        await write_file(error_s, f"errors_{client.myself.id}.txt")
        if msg:
            await msg.reply_document(
                f"errors_{client.myself.id}.txt",
                f"<b>All Errors Raised during the session and client {client.myself.first_name}_{client.myself.id}</b>",
            )
    await client.stop()
    return await log(
        f"<b>Added :</b> {added} \n<b>Failed :</b> {failed} \n<b>Privacy restricted :</b> {privacy_restricted} \n<b>Task Completed</b>",
        client,
        msg,
    )
