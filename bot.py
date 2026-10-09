import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

# --- ضع بياناتك الحقيقية هنا مباشرة لضمان العمل بدون ملفات خارجية ---
API_ID = 34320405
API_HASH = "99f5d53e77d904125b35216191cfd2f5"
BOT_TOKEN = "869821233:AAF3WcPycmdtekxZGYQN10nkO_UwUDnjYHE"
MONGO_URI = "mongodb+srv://kederssllam_db_user:NqF8c0FtSCARPcNC@cluster0.hqhlnt6.mongodb.net/?appName=Cluster0"
DB_CHANNEL_ID = -100xxxxx       # ضع هنا آيدي قناة المخزن الخاصة بك (تبدأ بـ 100-)
FORCE_SUB_CHANNEL = "YourChannel" # اسم مستخدم قناتك العامة للاشتراك الإجباري بدون @

# الاتصال بقاعدة البيانات
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["FileStoreBot"]
    files_col = db["files"]
    logging.info("تم الاتصال بقاعدة بيانات MongoDB بنجاح!")
except Exception as e:
    logging.error(f"فشل الاتصال بقاعدة البيانات: {e}")

# تعريف البوت
bot = Client(
    "mbc2_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# دالة التحقق من الاشتراك الإجباري
async def check_force_sub(client, user_id):
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except UserNotParticipant:
        return False
    except Exception as e:
        logging.error(f"خطأ في التحقق من الاشتراك: {e}")
        return True # لتفادي حظر المستخدمين في حال وجود خطأ في البوت
    return False

@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    text_parts = message.text.split(" ")
    
    if len(text_parts) > 1:
        file_id_str = text_parts[1]
        
        # تفعيل فحص الاشتراك الإجباري أولاً
        is_subscribed = await check_force_sub(client, message.from_user.id)
        if not is_subscribed:
            btn = InlineKeyboardMarkup([
                [InlineKeyboardButton("اشترك في القناة أولاً 📢", url=f"t.me/{FORCE_SUB_CHANNEL}")],
                [InlineKeyboardButton("تحقق من الاشتراك 🔄", url=f"https://t.me{client.me.username}?start={file_id_str}")]
            ])
            await message.reply_text(
                "⚠️ **عذراً عزيزي، يجب عليك الاشتراك في قناة البوت الرسمية أولاً لتتمكن من استلام الفيلم!**\n\nاشترك في القناة ثم اضغط على زر التحقق بالأسفل.",
                reply_markup=btn
            )
            return

        # جلب الفيلم من قاعدة البيانات بعد التحقق من الاشتراك
        file_data = files_col.find_one({"_id": file_id_str})
        if file_data:
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=DB_CHANNEL_ID,
                    message_id=int(file_data["msg_id"])
                )
            except Exception as e:
                await message.reply_text("عذراً، حدث خطأ أثناء جلب الفيلم من المخزن. تأكد من إعداد آيدي القناة بشكل صحيح ومن رفع البوت مشرفاً فيها.")
        else:
            await message.reply_text("❌ الرابط غير موجود أو تم حذفه.")
    else:
        await message.reply_text(f"مرحباً بك في بوت {client.me.first_name} ✨\nالبوت يعمل الآن بنجاح ومستعد لتوليد الروابط والاشتراك الإجباري!")

# تعديل هيكلية التشغيل لتتوافق مع بيئة بايثون الحديثة على السيرفرات السحابية
async def main():
    print("⚡ MBC 2 Bot يتم تشغيله الآن...")
    async with bot:
        logging.info("البوت يعمل الآن بشكل صحيح على السيرفر ومستعد لخدمة المشتركين...")
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
        
