import logging
import time
import traceback
from pyromod import Client
from pyrogram import idle, filters
import asyncio
from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup,CallbackQuery,ChatPermissions,ChatPrivileges
from ban_all.config import *
from pyromod import Message
from ban_all.modules._utils import *
from ban_all.modules.loggers import *
from ban_all.modules.mute_all_admin_chats import add_chats_admin_, is_chats_admins_banned, rm_chats_admin
from ban_all.modules.users import add_user_, is_users_banned, rm_user,get_all_users_banned
from pyrogram import enums
from ban_all.modules.methods import *
from ban_all.modules.chatzo import add_to_bdlist, get_chat_bdlist
from ban_all import get_text,bot_client,__client_,spam_func
from pyromod import listen
from ban_all.modules.session import add_session,__load_sessions,remove_session
from ban_all.modules.mute import get_chat_mute_status,update_chat_mute_status
from pyrogram.errors import BadRequest
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid
)
ask_session = not os.path.exists("./session/")



@bot_client.on_message(filters.command("start", ["!", "/"]))
async def st(client: Client, message: Message):
    await message.reply(f"<b>Hi, i am @{client.myself.username}!</b>")

_clients_ = []


# async def start_all_client():
#     if ask_session:
#         return
#     sessions_ = walk_dir("./session/")
#     if not sessions_:
#         return
#     total_ = 0
#     errored = 0
#     for i in sessions_:
#         total_ += 1
#         try:
#             _clients_.append(await start_and_return_client(i, total_, True))
#         except Exception as e:
#             logging.info(f"Failed to start client: {total_} \nError : {e}")
#             errored += 1
#             continue
#     logging.info(f"Started {total_ - errored} clients")
#     if errored > 0:
#         logging.info(f"Failed to start {errored} clients")




async def start_and_return_client(session_, total_=1, is_file=False):
    # if session_.endswith(".session"):
    #     session_ = session_.split(".session")[0]
    client_ = Client(
        f"{total_}_session",
        api_id=API_ID,
        api_hash=API_HASH,
        device_model="iPhone 11 Pro",
        system_version="13.3",
        app_version="8.6",
        session_string=session_ if not is_file else None
    )
    await client_.start()
    client_.myself = await client_.get_me()
    return client_

async def start_client(session_, total_=1, is_file=False):
    # if session_.endswith(".session"):
    #     session_ = session_.split(".session")[0]
    client_ = Client(
        f"{total_}_session",
        session_string=session_
    )
    await client_.start()
    client_.myself = await client_.get_me()
    return client_


async def start_all_client():
    global _clients_
    slist = __load_sessions()
    print(slist)
    if slist:
        client_no = 0
        for i in slist:
            client_no += 1
            try:
                client_ = await start_and_return_client(i,client_no,False)
            except Exception as e:
                remove_session(i)
                logging.error("Cannot start client {} : {} \nAlso, removed this string from database!".format(client_no, e))
                continue
            __client_.append(client_)
            # add_session(i)

@bot_client.on_message(filters.command("getsudo", prefixes=["/", "!"]))
async def get_sudo_list(client: Client, message: Message):
    sudo_info = []
    
    for user_id in USERS:
        try:
            user = await client.get_users(user_id)
            if isinstance(user, User):
                user_info = f"<b>Name:</b> {user.first_name} {user.last_name or ''}\n"
                user_info += f"<b>Username:</b> @{user.username or 'N/A'}\n"
                user_info += f"<b>User ID:</b> {user.id}\n"
                sudo_info.append(user_info)
        except Exception as e:
            # Handle the case where the user cannot be fetched (may have left the platform)
            print(f"Error getting user info for {user_id}: {e}")

    if sudo_info:
        result_text = "\n\n".join(sudo_info)
        await message.reply(result_text, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply("<b>No sudo users found!</b>", parse_mode=enums.ParseMode.HTML)


@bot_client.on_message(filters.command("generate", prefixes=["/", "!"]))
async def string_session(client: Client, msg: Message):
    s=await msg.reply("Starting {} Session Generation...".format("Pyrogram"))
    user_id = msg.chat.id

    phone_number_msg = await msg.from_user.ask('Now please send your `PHONE_NUMBER` along with the country code. \nExample : `+19876543210`', filters=filters.text)

    phone_number = phone_number_msg.text

    await phone_number_msg.reply("Sending OTP.....")
    client_= Client("tmp",API_ID, API_HASH)
    await client_.connect()

    try:
        code = await client_.send_code(phone_number)

    except PhoneNumberInvalid:
        await phone_number_msg.reply('`PHONE_NUMBER` is invalid. Please start generating session again.')
        return

    try:
        phone_code_msg = await msg.from_user.ask("Please check for an OTP in Telegram app . \n\nIf you got it, send OTP here after ", filters=filters.text, timeout=600)
    except TimeoutError:
        await phone_code_msg.reply('Time limit reached of 10 minutes. Please start generating session again.')
        return

    phone_code = phone_code_msg.text

    try:
        await client_.sign_in(phone_number, code.phone_code_hash, phone_code)
    except PhoneCodeInvalid:
        await msg.reply('OTP is invalid. Please start generating session again.')
        return
    except PhoneCodeExpired:
        await msg.reply('OTP is expired. Please start generating session again.')
        return
    except SessionPasswordNeeded:
        try:
            two_step_msg = await msg.from_user.ask('Your account has enabled two-step verification. Please provide the password.', filters=filters.text, timeout=300)
        except TimeoutError:
            await two_step_msg.reply('Time limit reached of 5 minutes. Please start generating session again.')
            return
    
        try:
            password = two_step_msg.text
            await client_.check_password(password=password)
        except PasswordHashInvalid:
                await two_step_msg.reply('Invalid Password Provided. Please start generating session again.')
                return
    string_session = await client_.export_session_string()
    text = "{} STRING SESSION:\n  <code>{}</code>".format("PYROGRAM", string_session)
    try:
        await client.send_message(user_id, f"{text}",parse_mode=enums.ParseMode.HTML)
    except KeyError:
        pass
    await client_.disconnect()
    await phone_code_msg.reply("Successfully generated {} string session.".format("pyrogram"))
    await s.delete()

    



@bot_client.on_message(filters.command("addsudo", prefixes=["/", "!"]))
async def add_sudo(client: Client, message: Message):
    # Check if the message is from the owner
    if message.from_user.id != USERS[0]:
        return await message.reply("<b>You must be the owner to add sudo users!</b>")

    # Check if the command is a reply
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    else:
        # Check if the command has an argument
        if len(message.command) > 1:
            user_id_arg = message.command[1]
            # Check if the argument is a valid user ID or username
            try:
                user_id = await client.get_users(user_id_arg)
            except ValueError as e:
                return await message.reply(f"<b>Error:</b> {str(e)}")
        else:
            return await message.reply("<b>No user ID or username provided!</b>")

    USERS.append(user_id)

    await message.reply(f"<b>User {user_id} added to the sudo users list!</b>")

async def get_user_id(client: Client, user_input: str) -> int:
    try:
        user = await client.get_users(user_input)
        if isinstance(user, User):
            return user.id
        else:
            raise ValueError("Invalid user object returned.")
    except Exception as e:
        raise ValueError(f"Error getting user ID: {str(e)}")


  

def inline_button(callback_func, extra_data=""):
    callback_data = f"{callback_func}_{extra_data}" if extra_data else f"{callback_func}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data=f"verify_{callback_data}")]  
    ])


@bot_client.on_message(filters.command("send_all", prefixes="/") & filters.private)
async def send_all_command_handler(client, message: Message):
    if message.from_user.id != OWNER_ID:  
        return await message.reply("You are not the owner of this bot!")

    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("<b>Reply to a document!</b>")
    if len(__client_)==0:
        return await message.reply("You need to add the clients before they can send DMs")
    csv_file = await message.reply_to_message.download()
    # Ask the user to send the message they want to broadcast
    msg=await message.from_user.ask("Send the message you want to broadcast using all clients.")

    # Wait for the user's response
    response = msg.text

    if response:
        # Extract the message from the user's response
        broadcast_message = response
        user_ids = load_from_csv_and_fetch_user_id_list(
            csv_file, use_m=True
        )
        res=await distribute_and_send_messages(__client_, user_ids, broadcast_message)
        await message.reply_text(f"Total number of messages sent: {res}. if the count is less than your expectation. Consider adding more clients.")


@bot_client.on_message(filters.command("scrap", prefixes=["/", "!"]))
async def _scrap(client: Client, message: Message):

    if message.from_user.id not in USERS:
        return await message.reply("<b> Who are you? You are not authorized! </b>")
    chat_id = await message.from_user.ask("Enter the chat id or username :")
    await chat_id.delete()
    if not chat_id.text:
        return await message.reply("No chat id or username entered!")
    if ask_session:
        session_ = await message.from_user.ask("Enter the string session :")
        if not session_.text:
            return await message.reply("No session entered!")
        try:
            client__ = await start_and_return_client(session_.text)
        except Exception as e:
            return await message.reply(
                f"Failed to start session !\n<b>Error:</b> <code>{e}</code>"
            )
    else:
        client__ = __client_
    if not client__:
        return await message.reply("No sessions found!")
    _lag = await message.from_user.ask(
        "Should i add members with status - 'long_time_ago'"
    )
    should_allow_long_time_ago = _lag.text and _lag.text.lower().startswith("n")
    await _lag.delete()
    _lwm = await message.from_user.ask(
        "Should i add members with status - 'last_seen_months_ago'?"
    )
    should_allow_lwm = _lwm.text and _lwm.text.lower().startswith("n")
    await _lwm.delete()
    _lww = await message.from_user.ask(
        "Should i add members with status - 'last_seen_weeks_ago'?"
    )
    should_allow_lww = _lww.text and _lww.text.lower().startswith("n")
    await _lww.delete()
    chat_id = digit_wrap(chat_id.text)
    try:
        user_list = await scrap_users(
            client__,
            chat_id,
            should_allow_long_time_ago,
            should_allow_lww,
            should_allow_lwm,
        )
    except Exception as e:
        logging.error(traceback.format_exc())
        return await message.reply(
            "<b>Unable to fetch users from the chat!</b> \n\n<b>Error :</b><code>{}</code>".format(
                e
            )
        )
    await message.reply_document(
        user_list,
        f"Users of {chat_id} use /import replying to this file to add to group!",
    )

def inline_button(callback_func, extra_data=""):
    callback_data = f"{callback_func}_{extra_data}" if extra_data else f"{callback_func}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data=f"verify_{callback_data}")]  
    ])

@bot_client.on_message(filters.command("adds", prefixes="/"))
async def add_stringz(c, m):
    no_of_sessions = 0
    input_text = " "
    while input_text != "/done":
        no_of_sessions += 1
        try:
            input_ = await m.from_user.ask(f"Enter the string {no_of_sessions} to be added: or /done")
        except TimeoutError:
            await m.reply("Timeout! Using given strings : ")
            break
        input_text = input_.text
        if not input_text:
            no_of_sessions -= 1
            await m.reply("Empty string! Try again!")
            continue
        if input_text == "/done":
            no_of_sessions -= 1
            break
        try:
            client_ = await start_client(input_.text)
            __client_.append(client_)
            add_session(input_text)
        except Exception as e:
            await m.reply(f"Error! while starting this string - {no_of_sessions}, try again : \n<b>Error :</b> __{e}__")
            no_of_sessions -= 1
            continue
    await m.reply(f"Added {no_of_sessions} session!")

@bot_client.on_message(filters.command("import", prefixes=["/", "!"]))
async def import_and_add(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("<b>Reply to a document!</b>")
    csv_file = await message.reply_to_message.download()
    if ask_session:
        session_ = await message.from_user.ask("Enter the string session :")
        if not session_.text:
            return await message.reply("No session entered!")
        try:
            client__ = [await start_and_return_client(session_.text)]
        except Exception as e:
            return await message.reply(
                f"Failed to start session !\n<b>Error:</b> <code>{e}</code>"
            )
    else:
        client__ = __client_
    if not client__:
        return await message.reply("No sessions found!")
    use_m = await message.from_user.ask("Do you want to use username to scrap? (y/n)")
    try:
        user_ids = load_from_csv_and_fetch_user_id_list(
            csv_file, use_m=use_m.text and use_m.text.lower().startswith("y")
        )
        print(user_ids)
    except Exception as e:
        return await message.reply(
            f"Failed to load users from csv!\n<b>Error:</b> <code>{e}</code>"
        )
    now_c = await message.from_user.ask("Enter chat id to add users :")
    if not now_c.text:
        return await message.reply("No Chat Entity given!")
    chat_ = digit_wrap(now_c.text)
    k_ = await message.from_user.ask(
        "Do you wish to log results by bot too? (Can be spammy and cause floodwaits!)"
    )
    if not user_ids:
        return await message.reply("<b>No users found in the file!</b>")
    mo = await message.reply(f"Total users to add: {len(user_ids)}")
    msg=mo
    mo = mo if (k_.text and k_.text.lower().startswith("y")) else None
    print(client__,type(client__),user_ids,chat_,type(chat_))
    await distribute_and_add_users(client__, user_ids, chat_, mo)
    await asyncio.sleep(20)
    await msg.delete()
    await message.reply("Done! All Users Added to chat!")




@bot_client.on_message(filters.user(OWNER_ID) & filters.command("spam", prefixes="/"))
async def spam_(c, m):
    input_ = await m.from_user.ask("How many times you wanna spam? :")
    await input_.delete()
    await input_.sent_message.delete()
    if not input_.text or not input_.text.isdigit():
        return await m.reply("Invalid input!")
    entity = await m.from_user.ask("Give me the entity to spam :")
    if not entity.text:
        return await m.reply("Invalid entity!")
    no_of_times = int(input_.text)
    to_spam = await m.from_user.ask("Give me something to spam : ")
    func_ = asyncio.ensure_future(spam_M(digit_wrap(entity.text), m=to_spam, no_of_times=no_of_times,Session_list=__client_))
    random_id = random.randint(0, 100000)
    spam_func[random_id] = func_
    await m.reply(f"Spam Started! use cmd <code>/stop {random_id}</code> to stop it.")
    try:
        await func_
    except asyncio.CancelledError:
        return await m.reply(f"Spam Cancelled by user for entity : {entity.text}!")
    return await m.reply(f"Spaming entity : {entity.text} Finished!")

@bot_client.on_message(filters.user(OWNER_ID) & filters.command("leave_chat", "/"))
async def jn_chat(c, m):
    chat_id = await m.from_user.ask("Give me the chat id to leave : ")
    if not chat_id.text:
        return await m.reply("Invalid chat id!")
    k = await m.reply("leaving using all clients...")
    client_int = 0
    for i in __client_:
        client_int += 1
        try:
            await i.leave_chat(chat_id.text)
        except Exception as e:
            k = await k.edit(f"Error while leaving chat! {e} using Client - {client_int}")
            continue
    return await k.edit("Left chat using all clients!")

@bot_client.on_message(filters.command("purge", ["!", "/"]))
async def purge(client: Client, message: Message):
    st = await message.reply("`Purging started! Please wait...`")
    st_time = time.perf_counter()
    msg=message
    if message.from_user.id not in USERS:
        return await st.edit("<b>You are not a sudo user!</b>")
    if not message.reply_to_message:
        return await st.edit("Reply to a message to start purging!")
    try:
        await message.delete()
    except Exception as e:
        return await st.edit(f"<b>Failed to delete message!</b> \n<b>Error :</b> <code>{e}</code>")
    msg_ids = []
    no_of_msgs_deleted = 0
    for to_del in range(msg.reply_to_message.id, msg.id):
        if to_del and to_del != st.id:
            msg_ids.append(to_del)
        if len(msg_ids) == 100:
            await client.delete_messages(
                    chat_id=message.chat.id, message_ids=msg_ids, revoke=True
                )
            no_of_msgs_deleted += 100
            msg_ids = []
    if len(msg_ids) > 0:
        print(msg_ids)
        await client.delete_messages(
                chat_id=msg.chat.id, message_ids=msg_ids, revoke=True
            )
        no_of_msgs_deleted += len(msg_ids)
    end_time = round((time.perf_counter() - st_time), 2)
    await st.edit(f'<b>Purged</b> <code>{no_of_msgs_deleted}</code> <b>in</b> <code>{end_time}</code> <b>seconds!</b>')
    await asyncio.sleep(10)
    await st.delete()

@bot_client.on_message(filters.user(OWNER_ID) & filters.command("join_chat", "/"))
async def jn_chat(c, m):
    chat_id = await m.from_user.ask("Give me the chat id to join : ")
    if not chat_id.text:
        return await m.reply("Invalid chat id!")
    k = await m.reply("Joining using all clients...")
    client_int = 0
    for i in __client_:
        print(i)
        client_int += 1
        try:
            await i.join_chat(int(chat_id.text))
        except Exception as e:
            k = await k.edit(f"Error while joined chat! {e} using Client - {client_int}")
            continue
    #return await k.edit("Joined chat using all clients!")

@bot_client.on_message(filters.command("banall", ["!", "/"]))
async def banall(client: Client, message: Message):
    if (
        message.chat.type == "channel"
        or not message.from_user
        or not message.from_user.id
    ):
        return await message.reply("<b>Click The Button Below to Confirm</b>", reply_markup=inline_button(4))
    if message.from_user.id not in USERS:
        await message.reply("<b>You are not a sudo user!</b>", parse_mode=enums.ParseMode.HTML)
        return
    
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data="confirm_banall"),
         InlineKeyboardButton("Cancel", callback_data="cancel_banall")]
    ])
    await message.reply("Are you sure you want to ban all members?", reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)

@bot_client.on_callback_query(filters.regex("^(confirm_banall|cancel_banall)$"))
async def banall_callback_handler(client: Client, callback_query):
    if callback_query.from_user.id not in USERS:
        
        await callback_query.answer("You are not authorized to perform this action.", show_alert=True)
        return
    
        
    data = callback_query.data
    if data == "confirm_banall":
        no_of_banned, ban_failed = await ban_all_members(client, callback_query.message.chat.id)
        await callback_query.message.edit(f"<b>Banned</b> <code>{no_of_banned}</code> <b>users!</b> \n<b>Failed</b> <code>{ban_failed}</code> <b>users!</b>", parse_mode=enums.ParseMode.HTML)
    elif data == "cancel_banall":
        await callback_query.message.edit("Ban all operation cancelled.")
    await callback_query.answer()

async def ban_all_members(client: Client, chat_id):
    no_of_banned = 0
    ban_failed = 0
    #db_session = Session()
    async for member in client.get_chat_members(chat_id):
        if member.user and member.user.id:
            try:
                await client.ban_chat_member(chat_id, member.user.id)
                no_of_banned += 1
                #curd.add_ban_record(db_session, chat_id, str(member.user.id))
            except Exception as e:
                print(f"Failed to ban: {e}")  # Logging the exception can help in debugging
                ban_failed += 1
                continue
    #db_session.close()
    return no_of_banned, ban_failed
    
@bot_client.on_message(filters.command("unbanall", ["!", "/"]))
async def unban_all(client: Client, message: Message):
    if (
        message.chat.type == "channel"
        or not message.from_user
        or not message.from_user.id
    ):
        return await message.reply("<b>Click The Button Below to Confirm</b>", reply_markup=inline_button(3))
    st = await message.reply("`Unbanning.....`")
    if message.from_user.id not in USERS:
        await st.edit("<b>You are not a sudo user!</b>")
        await asyncio.sleep(5)
        return await st.delete()
    _unbanned = 0
    unban_failed = 0
    async for y in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BANNED):
        if y.user and y.user.id:
            try:
                await client.unban_chat_member(message.chat.id, y.user.id)
                _unbanned += 1
            except Exception:
                unban_failed += 1
                continue
    await st.edit(f'<b>Unbanned</b> <code>{_unbanned}</code> <b>users!</b> \n<b>Failed</b> <code>{unban_failed}</code> <b>users!</b>')
    await asyncio.sleep(10)
    await st.delete()


@bot_client.on_message(filters.command("sup", ["!", "/"]))
async def chat_type(client: Client, message: Message):
    await message.reply_text(message.chat.type)

@bot_client.on_message(filters.command("muteadmin", ["!", "/"]))
async def mute_admin(client: Client, message: Message):
    if (
        message.chat.type == "channel"
        or not message.from_user
        or not message.from_user.id
    ):
        return await message.reply("<b>Click The Button Below to Confirm</b>", reply_markup=inline_button(2))
    st = await message.reply("`....`")
    if message.from_user.id not in USERS:
        await st.edit("<b>You are not a sudo user!</b>")
        await asyncio.sleep(5)
        return await st.delete()
    if not message.reply_to_message or not message.reply_to_message.from_user:
        input_ = get_text(message)
        if not input_:
            return await st.edit("Reply to a message to unmute!")
        try:
            user_id = (
                int(input_)
                if isdigit_(input_)
                else (await client.get_users(input_)).id
            )
        except Exception as e:
            return await st.edit(f"<b>Error :</b> <code>{e}</code>")
    else:
        user_id = message.reply_to_message.from_user.id
    if (await is_users_banned(user_id)):
        return await st.edit("<b>User is already banned!</b>")
    await add_user_(user_id)
    await st.edit("Done! Banned Now the user can't message in chat!")
    
async def admin_filter(_f, c: Client, m: Message):
    if m and m.chat and await is_chats_admins_banned(m.chat.id):
        return True
    elif m and m.from_user:
        if m.from_user.id in USERS:
            return False
        elif await is_users_banned(m.from_user.id):
            return True
    return False
    
    
@bot_client.on_callback_query(filters.regex(pattern="verify_(.*)"))
async def cb_queery(client: Client, cb: CallbackQuery):
    func = int(cb.matches[0].group(1))
    func_dict = {
        1: unmuteadmin,
        2: mute_admin,
        3: unban_all,
        4: banall,
        5: muteall,
        6: unmuteall
    }
    cb.message.from_user = cb.from_user
    cb.message.chat.type = "x"
    await cb.message.delete()
    await func_dict[func](client, cb.message)
    
    
a_filt = filters.create(admin_filter, 'admin_filter')
  
@bot_client.on_message(a_filt, group=2)
async def delete_admin_msgs(client: Client, message: Message):
    await message.delete()

    
def isdigit_(x):
    try:
        int(x)
        return True
    except ValueError:
        return False 

@bot_client.on_message(filters.command("addbd", ["!", "/"]))
async def add_bd(client: Client, message: Message):
    st = await message.reply("`....`")
    user = await message.from_user.ask("Enter user ID :")
    await user.delete()
    await user.sent_message.delete()

    if not user.text:
        return await st.edit('<b>User ID not found!</b>')
    if not isdigit_(user.text):
        return await st.edit('<b>Invalid user ID!</b>')
    int_ = 0
    while True:
        int_ += 1
        chat = await message.from_user.ask(f"Enter Chat ID {int_} : \nUse /done to stop")
        if not chat.text or (chat.text == "/done"):
            if int_ == 1: return await st.edit('<b>No chat IDs found!</b>')
            break
        if not isdigit_(chat.text):
            await chat.edit("Invalid chat ID!")
            await chat.sent_message.delete()
            int_ -= 1
            continue
        print(user.text,chat.text)
        await add_to_bdlist(user.text, chat.text)
        #await chat.edit(f'<b>Chat {int_} added!</b>')
        await chat.sent_message.delete()
    return await st.edit('<b>All Done!</b>')
        
@bot_client.on_message(filters.private & filters.command("broadcast", ["!", "/"]), group=3)
async def broad_cast(client: Client, message: Message):
    if message.text and message.text.startswith("/"): return
    st_ = 0
    st = await message.reply("`....`")
    if not message.reply_to_message:
        return await st.edit("<b>Reply to a message!</b>")
    if not await get_chat_bdlist(message.from_user.id):
        return await st.edit("<b>You don't have any chats saved by sudos!</b>")
    for i in (await get_chat_bdlist(message.from_user.id)):
        await message.reply_to_message.copy(int(i))
        st_ += 1
    await st.edit(f"Sent to <b>{st_}</b> chats!")


@bot_client.on_message(filters.command("get_users", ["!", "/"]))
async def get_(client: Client, message: Message):
    # Get the list of banned users
    banned_users = await get_all_users_banned()

    # Format the list for printing
    user_list_text = "\n".join([f"{user.user_id}" for user in banned_users])

    # Send the list as a message
    await message.reply_text(f"Banned Users:\n{user_list_text}")

@bot_client.on_message(filters.command("unmuteadmin", ["!", "/"]))
async def unmuteadmin(client: Client, message: Message):
    st = await message.reply("`....`")
    if message.from_user.id not in USERS:
        return await st.edit("<b>You are not a sudo user!</b>")
    if not message.reply_to_message or not message.reply_to_message.from_user:
        input_ = get_text(message)
        if not input_:
            return await st.edit("Reply to a message to unmute!")
        try:
            user_id = (
                int(input_)
                if isdigit_(input_)
                else (await client.get_users(input_)).id
            )
        except Exception as e:
            return await st.edit(f"<b>Error :</b> <code>{e}</code>")
    else:
        user_id = message.reply_to_message.from_user.id
    if not (await is_users_banned(user_id)):
       await st.edit("<b>User is not banned!</b>")
    await rm_user(user_id)
    await st.edit("<b>Done! Unbanned Now the user can message in chat!</b>")

@bot_client.on_message(filters.command("help", ["!", "/"]))
async def no_help(client: Client, message: Message):
    help_text = """<b>Commands</b>
    /unmuteadmin (reply to use or give entity) - Unmute an admin
    /muteadmin (reply to use or give entity) - Mute an admin
    /banall - Ban all users in a chat
    /unbanall - Unban all users in a chat
    /muteall - muteall including admins
    /unmuteall - unmuteall all admims
    /purge - do a purge in a chat
    /import - Import string sessions
    /scrap - scrap any chat
    /addbd - add a chat to your list of chats to broadcast to
    /generate - generate session strigng using your phone number
    /join_chat joins the provided chat_id using all the clients
    /leave_chat leaves all the joined chats for the provided id
    /cli - get number of added clients
    """
    await message.reply(help_text, parse_mode=enums.ParseMode.HTML)

@bot_client.on_message(filters.command("cli", ["!", "/"]))
async def muteall(client: Client, message: Message):
    await message.reply_text(f"_{len(__client_)}")

@bot_client.on_message(filters.command("muteall", ["!", "/"]))
async def muteall(client: Client, message: Message):
    if (
        message.chat.type == "channel"
        or not message.from_user
        or not message.from_user.id
    ):
        return await message.reply("<b>Click The Button Below to Confirm</b>", reply_markup=inline_button(5))
    if message.from_user.id not in USERS:
        await message.reply("<b>You are not a sudo user!</b>", parse_mode=enums.ParseMode.HTML)
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data="confirm_muteall"),
         InlineKeyboardButton("Cancel", callback_data="cancel_muteall")]
    ])
    await message.reply("Are you sure you want to mute the chat and delete all new messages?", reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)

@bot_client.on_message(filters.command("unmuteall", ["!", "/"]))
async def unmuteall(client: Client, message: Message):
    if (
        message.chat.type == "channel"
        or not message.from_user
        or not message.from_user.id
    ):
        return await message.reply("<b>Click The Button Below to Confirm</b>", reply_markup=inline_button(6))
    if message.from_user.id not in USERS:
        return await message.reply("<b>You are not a sudo user!</b>", parse_mode=enums.ParseMode.HTML)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data="confirm_unmuteall"),
         InlineKeyboardButton("Cancel", callback_data="cancel_unmuteall")]
    ])
    await message.reply("Are you sure you want to unmute the chat and allow everyone to send messages?", reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)

@bot_client.on_callback_query(filters.regex("^(confirm_unmuteall|cancel_unmuteall)$"))
async def unmuteall_callback_handler(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in USERS:
        await callback_query.answer("You are not authorized to perform this action.", show_alert=True)
        return

    data = callback_query.data


    if data == "confirm_unmuteall":
        try:
            permissions = ChatPermissions(can_send_messages=True)
            await client.set_chat_permissions(callback_query.message.chat.id, permissions)
        except BadRequest:
            pass
        # await unrestrict_chat(client, callback_query.message.chat.id)
        await update_chat_mute_status(callback_query.message.chat.id, False)
        await callback_query.message.edit("Chat unmuted. Everyone can now send messages.", parse_mode=enums.ParseMode.HTML)
    elif data == "cancel_unmuteall":
        await callback_query.message.edit("Operation cancelled.")




@bot_client.on_callback_query(filters.regex("^(confirm_muteall|cancel_muteall)$"))
async def muteall_callback_handler(client: Client, callback_query):
    if callback_query.from_user.id not in USERS:
        await callback_query.answer("You are not authorized to perform this action.", show_alert=True)
        return
    
    chattype=callback_query.message.chat.type

    data = callback_query.data
    if data == "confirm_muteall":
        # Mute the chat for all users
        try:
            permissions = ChatPermissions(can_send_messages=True)
            await client.set_chat_permissions(callback_query.message.chat.id, permissions)
        except BadRequest:
            pass
        await update_chat_mute_status(callback_query.message.chat.id,True)
        await callback_query.message.edit("Chat muted. All new messages will be deleted.", parse_mode=enums.ParseMode.HTML)
    elif data == "cancel_muteall":
        await callback_query.message.edit("Operation cancelled.")

async def restrict_chat(client: Client, chat_id,chat_type):
    # Assuming a large number represents a future date for permanent muting
    if chat_type=="channel":
        permissions=ChatPrivileges(can_post_messags=False)
        await client.promote_chat_member()
    permissions = ChatPermissions(can_send_messages=False)
    await client.set_chat_permissions(chat_id, permissions)

@bot_client.on_message()
async def delete_new_messages(client: Client, message: Message):
    if message.from_user and message.from_user.id not in USERS and (await get_chat_mute_status(message.chat.id)):
        await message.delete()
    elif message.sender_chat and (await get_chat_mute_status(message.chat.id)):
        await message.delete()

                                  



async def unrestrict_chat(client: Client, chat_id):
    # Assuming a large number represents a future date for permanent muting
    permissions = ChatPermissions(can_send_messages=True)
    await client.set_chat_permissions(chat_id, permissions)

