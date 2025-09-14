from telegram import Bot

BOT_TOKEN = "8344896751:AAE8__3bTY4wEs5mzvItr9-Rm5cGdkrJhQk"  # paste the token BotFather gave you

bot = Bot(token=BOT_TOKEN)

# this gets info about the most recent message you sent the bot
updates = bot.get_updates()

for u in updates:
    print(u.message.chat.id, u.message.chat.first_name)