import asyncio
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# لازم يكون قبل إنشاء Client (حل مشكلة event loop)
asyncio.set_event_loop(asyncio.new_event_loop())

from hydrogram import Client, filters
from hydrogram.enums import ChatMemberStatus
from hydrogram.errors import UserNotParticipant
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

# يقرأ من متغيرات البيئة أولاً، وإذا ما لقاها بياخد القيم الافتراضية
API_ID = int(os.environ.get("API_ID", "34320405"))
API_HASH = os.environ.get("API_HASH", "99f5d53e77d904125b35216191cfd2f5")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8698291233:AAEvVnETbqJOQ-7_cHSX2MZbP8dxkywmpDo")
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://kederssllam_db_user:NqF8c0FtSCARPcNC@cluster0.hqhlnt6.mongodb.net/?appName=Cluster0",
)

DB_CHANNEL_ID = -1003921766270
FORCE_SUB_CHANNEL = "MBC2_MOVIE"  # اكتب none لتعطيل الاشتراك الإجباري

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["FileStoreBot"]
files_col = db["files"]
logging.info("MongoDB Connected Successfully!")

bot = Client(
    "mbc2_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


# سيرفر صغير حتى ما يعمل Render Timeout إذا الخدمة من نوع Web Service
class _Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, *args):
        pass


def _run_health_server():
    port = int(os.environ.get("PORT", "10000"))
    HTTPServer(("0.0.0.0", port), _Health).serve_forever()


async def check_force_sub(client, user_id):
    if FORCE_SUB_CHANNEL.lower() == "none":
        return True
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        )
    except UserNotParticipant:
        return False
    except Exception as e:
        logging.error(f"Sub Check Error: {e}")
        return True


@bot.on_message(filters.channel, group=1)
async def debug_channel(client, message: Message):
    # سطر تشخيصي: بيطبع ID أي قناة البوت شايفها (بتقدر تشيله بعدين)
    logging.info(f"CHANNEL POST | id={message.chat.id} | title={message.chat.title} | media={message.media}")


@bot.on_message(filters.chat(DB_CHANNEL_ID) & (filters.document | filters.video))
async def archive_and_link(client, message: Message):
    logging.info(f"Archiving message {message.id}")
    file_id_str = str(message.id)

    files_col.update_one(
        {"_id": file_id_str},
        {"$set": {"msg_id": message.id, "caption": message.caption or ""}},
        upsert=True,
    )

    bot_user = (await client.get_me()).username
    deep_link = f"https://t.me/{bot_user}?start={file_id_str}"

    await message.reply_text(
        f"✅ **تمت أرشفة الفيلم بنجاح!**\n\n🔗 **رابط التوجيه العميق:**\n`{deep_link}`",
        disable_web_page_preview=True,
    )


@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    text_parts = message.text.split(" ")

    if len(text_parts) > 1:
        file_id_str = text_parts[1]

        if not await check_force_sub(client, message.from_user.id):
            bot_user = (await client.get_me()).username
            btn = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Join Channel / انضم للقناة 📢", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
                    [InlineKeyboardButton("Try Again / حاول مجدداً 🔄", url=f"https://t.me/{bot_user}?start={file_id_str}")],
                ]
            )
            await message.reply_text(
                "⚠️ **عذراً عزيزي، يجب عليك الاشتراك في قناتنا أولاً لتتمكن من تحميل ومشاهدة الفيلم!**\n\n"
                "اشترك بالقناة ثم اضغط على زر (حاول مجدداً).",
                reply_markup=btn,
            )
            return

        file_data = files_col.find_one({"_id": file_id_str})
        if file_data:
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=DB_CHANNEL_ID,
                    message_id=int(file_data["msg_id"]),
                )
            except Exception as e:
                logging.error(f"Copy Error: {e}")
                await message.reply_text("❌ عذراً، حدث خطأ أثناء جلب الفيلم.")
        else:
            await message.reply_text("❌ هذا الرابط غير موجود.")
    else:
        await message.reply_text(
            "✨ مرحباً بك في بوت أرشفة وتسليم الأفلام التلقائي!\n\nالبوت يعمل الآن بنجاح."
        )


if __name__ == "__main__":
    threading.Thread(target=_run_health_server, daemon=True).start()
    bot.run()
    
