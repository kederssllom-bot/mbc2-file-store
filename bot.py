import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from fastapi import FastAPI
import uvicorn
from threading import Thread

# البيانات الخاصة بك
BOT_TOKEN = "869821233:AAF3WcPycmdtekxZGYQN10nkO_UwUDnjYHE"
API_ID = 34320405
API_HASH = "99f5d53e77d904125b35216191cfd2f5"
MONGO_URI = "mongodb+srv://kederssllam_db_user:NqF8c0FtSCARPcNC@cluster0.hqhlnt6.mongodb.net/?appName=Cluster0"

db_client = MongoClient(MONGO_URI)
db = db_client["MBC2_Bot_DB"]
files_collection = db["stored_files"]

app = Client("mbc2_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# خادم ويب وهمي لإرضاء سيرفر Render المجاني
web_app = FastAPI()

@web_app.get("/")
def read_root():
    return {"status": "Bot is running successfully"}

@app.on_message(filters.command("start"))
async def start_command(client, message):
    text = message.text
    if len(text) > 7:
        file_id_key = text.split(" ")[1]
        file_data = files_collection.find_one({"file_key": file_id_key})
        
        if file_data:
            await client.send_cached_media(chat_id=message.chat.id, file_id=file_data["file_id"])
            await message.reply_text("📥 تم إرسال الفيلم بنجاح! مشاهدة ممتعة.")
        else:
            await message.reply_text("❌ عذراً، هذا الرابط غير صالح أو تم حذفه.")
    else:
        await message.reply_text(f"👋 أهلاً بك في بوت {message.from_user.mention}\nأرسل لي أي ملف أو فيلم لتخزينه وتوليد رابط له.")

@app.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def save_file(client, message):
    file_key = str(message.id)
    media_type = message.media.value
    file_id = getattr(message, media_type).file_id
    
    files_collection.insert_one({"file_key": file_key, "file_id": file_id})
    
    bot_username = "MBC2_Movies_bot"
    share_link = f"https://t.me{bot_username}?start={file_key}"
    
    await message.reply_text(
        f"✅ **تم حفظ الفيلم في المخزن بنجاح!**\n\n🔗 **رابط المشاهدة الخاص بك:**\n`{share_link}`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 مشاركة الرابط", url=f"https://t.meshare/url?url={share_link}")]
        ])
    )

def run_web():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(web_app, host="0.0.0.0", port=port)

async def start_bot():
    print("⚡ البوت يبدأ التشغيل الآن...")
    await app.start()
    print("✅ البوت يعمل بنجاح ومستعد لاستقبال الملفات!")

if __name__ == "__main__":
    # تشغيل خادم الـ Web في مسار مستقل
    Thread(target=run_web, daemon=True).start()
    
    # تشغيل البوت التليجرام
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
    loop.run_forever()
    
