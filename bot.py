import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant
from pymongo import MongoClient
import config

logging.basicConfig(level=logging.INFO)

# الاتصال بقاعدة البيانات
try:
    mongo_client = MongoClient(config.MONGO_URI)
    db = mongo_client["FileStoreBot"]
    files_col = db["files"]
    logging.info("تم الاتصال بقاعدة بيانات MongoDB بنجاح!")
except Exception as e:
    logging.error(f"فشل الاتصال بقاعدة البيانات: {e}")

# تعريف البوت
bot = Client(
    "mbc2_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    if len(message.command) > 1:
        file_id_str = message.command[1]
        file_data = files_col.find_one({"_id": file_id_str})
        
        if file_data:
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=config.DB_CHANNEL_ID,
                    message_id=int(file_data["msg_id"])
                )
            except Exception as e:
                await message.reply_text("عذراً، حدث خطأ أثناء جلب الفيلم من المخزن. تأكد من إعداد آيدي القناة بشكل صحيح.")
        else:
            await message.reply_text("❌ الرابط غير موجود أو تم حذفه.")
    else:
        await message.reply_text(f"مرحباً بك في بوت {client.me.first_name} ✨\nالبوت يعمل الآن بنجاح ومستعد لتوليد الروابط!")

async def main():
    async with bot:
        logging.info("البوت يعمل الآن بشكل صحيح على السيرفر...")
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
        
