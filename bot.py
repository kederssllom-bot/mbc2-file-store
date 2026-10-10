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
BOT_TOKEN = "8698291233:AAEvVnETbqJOQ-7_cHSX2MZbP8dxkywmpDo"
MONGO_URI = "mongodb+srv://kederssllam_db_user:NqF8c0FtSCARPcNC@cluster0.hqhlnt6.mongodb.net/?appName=Cluster0"

DB_CHANNEL_ID = -1003921766270  
FORCE_SUB_CHANNEL = "MBC2_MOVIE"  

try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["FileStoreBot"]
    files_col = db["files"]
    logging.info("MongoDB Connected Successfully!")
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

@bot.on_message(filters.chat(DB_CHANNEL_ID) & (filters.document | filters.video))
async def archive_and_link(client, message: Message):
    file_id_str = str(message.id)
    
    # استخدام الصيغة المباشرة للـ MongoDB بدون أي رموز هروب
    files_col.update_one(
        {"_id": file_id_str},
        {"\$set": {"msg_id": message.id, "caption": message.caption or ""}},
        upsert=True
    )
    
    bot_user = (await client.get_me()).username
    deep_link = f"https://t.me{bot_user}?start={file_id_str}"
    
    await message.reply_text(
        f"✅ **تمت أرشفة الفيلم بنجاح!**\n\n🔗 **رابط التوجيه العميق:**\n`{deep_link}`",
        disable_web_page_preview=True
    )

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    text_parts = message.text.split(" ")
    
    if len(text_parts) > 1:
        file_id_str = text_parts[1]
        
        is_subscribed = await check_force_sub(client, message.from_user.id)
        if not is_subscribed:
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel / انضم للقناة 📢", url=f"https://t.me{FORCE_SUB_CHANNEL}")],
                [InlineKeyboardButton("Try Again / حاول مجدداً 🔄", url=f"https://t.me{(await client.get_me()).username}?start={file_id_str}")]
            ])
            await message.reply_text(
                "⚠️ **عذراً عزيزي، يجب عليك الاشتراك في قناتنا أولاً لتتمكن من تحميل ومشاهدة الفيلم!**\n\nاشترك بالقناة ثم اضغط على زر (حاول مجدداً).", 
                reply_markup=btn
            )
            return

        file_data = files_col.find_one({"_id": file_id_str})
        if file_data:
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=DB_CHANNEL_ID,
                    message_id=int(file_data["msg_id"])
                )
            except Exception as e:
                await message.reply_text("❌ عذراً، حدث خطأ أثناء جلب الفيلم.")
        else:
            await message.reply_text("❌ هذا الرابط غير موجود.")
    else:
        await message.reply_text(f"✨ مرحباً بك في بوت أرشفة وتسليم الأفلام التلقائي!\n\nالبوت يعمل الآن بنجاح.")

# 🛠️ الحل الجذري لإنهاء مشكلة حلقة الأحداث (Event Loop) على بايثون الحديثة
if __name__ == "__main__":
    try:
        # إجبار الكود على إنشاء وإدارة حلقة أحداث مخصصة بدون الاعتماد على الإعداد التلقائي المحظور بالسيرفر
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot.run())
    except KeyboardInterrupt:
        sys.exit(0)
        
