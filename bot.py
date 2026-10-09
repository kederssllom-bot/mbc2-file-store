import os
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

# --- CONFIGURATION ---
API_ID = 34320405
API_HASH = "99f5d53e77d904125b35216191cfd2f5"
BOT_TOKEN = "869821233:AAF3WcPycmdtekxZGYQN10nkO_UwUDnjYHE"
MONGO_URI = "mongodb+srv://kederssllam_db_user:NqF8c0FtSCARPcNC@cluster0.hqhlnt6.mongodb.net/?appName=Cluster0"

# Optional Channel Settings (Update these with your actual IDs)
# CHANNEL_ID = -100xxxxxxxxx (Your private storage channel)
# AUTH_CHANNEL = -100xxxxxxxxx (Your forcesub channel)

# --- INITIALIZATION ---
app = Client("movie_store_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
db_client = MongoClient(MONGO_URI)
db = db_client["MBC2_Movies_bot"]
files_col = db["stored_files"]

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    text = message.text
    # Check for deep linking
    if len(text.split()) > 1:
        file_id_str = text.split()[1]
        
        # --- Force Subscribe Check Example ---
        # try:
        #     user = await client.get_chat_member(AUTH_CHANNEL, message.from_user.id)
        #     if user.status == "kicked":
        #         await message.reply_text("عذراً، أنت محظور من استخدام البوت.")
        #         return
        # except Exception:
        #     btn = [[InlineKeyboardButton("اشترك في القناة أولاً 📢", url=f"https://t.me/your_channel_username")]]
        #     await message.reply_text("يجب عليك الاشتراك في قناة البوت الرسمية أولاً لتتمكن من تحميل الفيلم!", reply_markup=InlineKeyboardMarkup(btn))
        #     return

        # Fetch from DB
        file_data = files_col.find_one({"_id": file_id_str})
        if file_data:
            await client.send_cached_media(
                chat_id=message.chat.id,
                file_id=file_data["file_id"],
                caption=file_data.get("caption", "")
            )
        else:
            await message.reply_text("❌ عذراً، هذا الرابط منتهي الصلاحية أو تم حذف الملف من قاعدة البيانات.")
    else:
        await message.reply_text(
            f"👋 مرحباً بك {message.from_user.mention} في بوت **MBC 2 Bot** أرشيف ومخزن الأفلام.\n\n"
            "قم بتوجيه أي فيلم أو ملف من قناتك الخاصة إلى هنا ليقوم البوت بحفظه وتوليد رابط تحميل مباشر للمشاهدين."
        )

@app.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def save_file_handler(client, message):
    file_type = message.media.value
    media = getattr(message, file_type)
    file_id = media.file_id
    caption = message.caption if message.caption else ""
    
    # Store in DB using unique file_id prefix or message id
    doc_id = str(message.id)
    files_col.update_one(
        {"_id": doc_id},
        {"$set": {"file_id": file_id, "caption": caption, "type": str(file_type)}},
        upsert=True
    )
    
    bot_username = (await client.get_me()).username
    deep_link = f"https://t.me/{bot_username}?start={doc_id}"
    
    await message.reply_text(
        f"✅ **تم حفظ الفيلم بنجاح في قاعدة البيانات!**\n\n"
        f"🔗 **رابط التحميل الخاص بالمشاهدين:**\n`{deep_link}`\n\n"
        "يمكنك نسخ هذا الرابط ووضعه في زر شفاف تحت بوستر الفيلم في قناتك العامة.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 رابط الفيلم", url=deep_link)]])
    )

if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run()