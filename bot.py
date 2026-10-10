import asyncio
import logging
import sys
from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from hydrogram.errors import UserNotParticipant
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

API_ID = 34320405
API_HASH = "99f5d53e77d904125b35216191cfd2f5"
BOT_TOKEN = "8698291233:AAFfzY_IIMOwzQ5LFcm_fSvzcaO3jR44vX8"
MONGO_URI = "mongodb+srv://kederssllam_db_user:NqF8c0FtSCARPcNC@cluster0.hqhlnt6.mongodb.net/?appName=Cluster0"

# الإعدادات الصحيحة والنهائية لقنواتك
DB_CHANNEL_ID = -1003921766270  
FORCE_SUB_CHANNEL = "MBC2_MOVIE"  

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

# دالة فحص الاشتراك الإجباري
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

# ⭐ الدالة الجديدة والمهمة جداً: استقبال الرسائل في المخزن وأرشفتها وتوليد روابط التوجيه العميق تلقائياً
@bot.on_message(filters.chat(DB_CHANNEL_ID) & (filters.document | filters.video))
async def archive_and_link(client, message: Message):
    file_id_str = str(message.id)
    
    # حفظ آيدي الفيلم في MongoDB
    files_col.update_one(
        {"_id": file_id_str},
        {"\$set": {"msg_id": message.id, "caption": message.caption or ""}},
        upsert=True
    )
    
    # جلب يوزر نيم البوت وتوليد الرابط العميق للفيلم
    bot_user = (await client.get_me()).username
    deep_link = f"https://t.me/{bot_user}?start={file_id_str}"
    
    # إرسال الرابط كرد في قناة المخزن لنسخه ووضعه في قناة البوسترات العامة
    await message.reply_text(
        f"✅ **تمت أرشفة الفيلم بنجاح!**\n\n🔗 **رابط التوجيه العميق:**\n`{deep_link}`",
        disable_web_page_preview=True
    )

# معالجة أمر البداية والروابط العميقة في الخاص
@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    text_parts = message.text.split(" ")
    
    if len(text_parts) > 1:
        file_id_str = text_parts[1]
        
        # التحقق من الاشتراك الإجباري
        is_subscribed = await check_force_sub(client, message.from_user.id)
        if not is_subscribed:
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel / انضم للقناة", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
                [InlineKeyboardButton("Try Again / حاول مجدداً", url=f"https://t.me/{(await client.get_me()).username}?start={file_id_str}")]
            ])
            await message.reply_text(
                "⚠️ **عذراً، يجب عليك الاشتراك في قناتنا أولاً للحصول على الفيلم.**\n\nJoin our channel to get the movie.", 
                reply_markup=btn
            )
            return

        # جلب البيانات من MongoDB
        file_data = files_col.find_one({"_id": file_id_str})
        if file_data:
            try:
                # إرسال الفيلم للمستخدم كنسخة دون إظهار القناة المخفية كـ مصدر
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=DB_CHANNEL_ID,
                    message_id=int(file_data["msg_id"])
                )
            except Exception as e:
                await message.reply_text("Error retrieving file.")
                logging.error(f"Copy message error: {e}")
        else:
            await message.reply_text("Link not found.")
    else:
        await message.reply_text(f"Welcome to {client.me.first_name}\nBot is running successfully.")

# دالة التشغيل المستقرة والآمنة
async def main():
    await bot.start()
    logging.info("Bot is active and running successfully!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
        
