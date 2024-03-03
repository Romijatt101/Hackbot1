**Setting Up the UserBot:**

Before you can use the UserBot, you need to set it up with your own credentials. Follow these steps:

1. **Create a Telegram Application:**
   - Go to the [Telegram Developer Portal](https://my.telegram.org/auth).
   - Log in with your Telegram account.
   - Create a new application and note down the `API_ID` and `API_HASH`.

2. **Create a Bot:**
   - Talk to [@BotFather](https://t.me/BotFather) on Telegram.
   - Use the `/newbot` command to create a new bot.
   - Note down the provided `BOT_TOKEN`.

3. **Get Your User ID:**
   - Talk to [@userinfobot](https://t.me/userinfobot) on Telegram.
   - It will provide you with your User ID. Note it down.

4. **Database URL:**
   - Set up a database for the UserBot. You can use your preferred database service.
   - Replace `DB_URL` with the URL of your database. You can get it from [Elephant SQL](https://www.elephantsql.com/) or create a PostgreSQL link from [Railway.app](https://railway.app/).

5. **Owner ID:**
   - Replace `OWNER_ID` with the User ID you obtained from [@userinfobot](https://t.me/userinfobot).

6. **Configure the UserBot:**
   - Open the UserBot script in your preferred code editor.
   - Replace `API_ID`, `API_HASH`, `BOT_TOKEN`, `DB_URL`, and `OWNER_ID` with your credentials.
   - Additionally, you can add specific user IDs to the `USERS` list if needed.

7. **Run the UserBot:**
   - Deploy the UserBot script in your preferred environment.
   - Make sure to install all required dependencies.
   - Run the script.

8. **Test Commands:**
   - Once the UserBot is running, you can test commands such as `/generate`, `/join_chat`, etc.
   - Ensure that the UserBot responds correctly and performs actions as expected.

Remember to keep your credentials secure and not share them with others. If you encounter any issues during setup, refer to the UserBot documentation or seek assistance from the community.

Now, you're ready to use the UserBot with your customized settings! 

**UserBot Commands:**

- `/unmuteadmin (reply to user or give entity)`: Unmute an admin.
- `/muteadmin (reply to user or give entity)`: Mute an admin.
- `/banall`: Ban all users in a chat.
- `/unbanall`: Unban all users in a chat.
- `/muteall`: Mute all, including admins.
- `/unmuteall`: Unmute all admins.
- `/purge`: Purge messages in a chat.
- `/import`: Add users from a CSV file to the target.
- `/scrap`: Scrap any chat.
- `/addbd`: Add a chat to your list of chats to broadcast to.
- `/generate`: Generate a session string using your phone number.
- `/join_chat <chat_id>`: Join the provided chat_id using all the clients.
- `/leave_chat <chat_id>`: Leave all the joined chats for the provided ID.
- `/cli`: Get the number of added clients.
- `/spam`: To be used after `/join_chat`, spam multiple times the spam message to the target entity.

**Caution:**
Using the UserBot maliciously or against Telegram's policies can lead to the permanent suspension of your account. Please use these commands responsibly and adhere to Telegram's guidelines.

**Credits:**
[@freakyLuffy](https://github.com/freakyLuffy) | [@Teameviral](https://github.com/Teameviral)
