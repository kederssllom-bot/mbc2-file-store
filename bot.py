import asyncio
import logging
import sys
import nest_asyncio  # استيراد المكتبة لحل تداخل حلقات الأحداث
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant
from pymongo import MongoClient

# تفعيل المكتبة فوراً لحل مشكلة 'There is no current event loop'
nest_asyncio.apply()

# تهيئة نظام asyncio بالطريقة المتوافقة مع السيرفرات الحديثة
if sys.platform != 'win32':
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

logging.basicConfig(level=logging.INFO)

API_ID = 34320405
API_HASH = "99f5d53e77d904125b35216191cfd2f5"
BOT_TOKEN = "8698291233:AAFfzY_IIMOwzQ5LFcm_fSvzcaO3jR44vX8"
MONGO_URI = "mongodb+srv://kederssllam_db_user:NqF8c0FtSCARPcNC@cluster0.hqhlnt6.mongodb.net/?appName=Cluster0"

DB_CHANNEL_ID = 0
FORCE_SUB_CHANNEL = "none"

try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["FileStoreBot"]
    files_col = db["files"]
    logging.info("MongoDB Connected")
except Exception as e:
    logging.error(f"DB Error: {e}")

bot = Client(
    "mbc2_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

async def check_force_sub(client, user_id):
    if FORCE_SUB_CHANNEL == "none":
        return True
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except UserNotParticipant:
        return False
    except Exception as e:
        logging.error(f"Sub Check Error: {e}")
        return True
    return False

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    text_parts = message.text.split(" ")
    
    if len(text_parts) > 1:
        file_id_str = text_parts[1]
        
        is_subscribed = await check_force_sub(client, message.from_user.id)
        if not is_subscribed:
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel", url=f"t.me/{FORCE_SUB_CHANNEL}")],
                [InlineKeyboardButton("Try Again", url=f"https://t.me{client.me.username}?start={file_id_str}")]
            ])
            await message.reply_text("Join our channel to get the movie.", reply_markup=btn)
            return

        file_data = files_col.find_one({"_id": file_id_str})
        if file_data and DB_CHANNEL_ID != 0:
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=DB_CHANNEL_ID,
                    message_id=int(file_data["msg_id"])
                )
            except Exception as e:
                await message.reply_text("Error retrieving file.")
        else:
            await message.reply_text("Link not found.")
    else:
        await message.reply_text(f"Welcome to {client.me.first_name}\nBot is running successfully.")

async def start_bot():
    await bot.start()
    logging.info("Bot is active and running...")
    # حلقة حجز مستمرة تمنع البوت من الإغلاق
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    # تشغيل آمن ونظيف تماماً
    asyncio.run(start_bot())
    
