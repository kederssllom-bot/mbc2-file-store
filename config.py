import os

# بيانات تليجرام والمفاتيح الخاصة بمشروعك (مأخوذة تلقائياً أو من السيرفر)
API_ID = int(os.environ.get("API_ID", 34320405))
API_HASH = os.environ.get("API_HASH", "99f5d53e77d904125b35216191cfd2f5")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8698291233:AAEvVnETbqJOQ-7_cHSX2MZbP8dxkywmpDo")

# رابط قاعدة بيانات MongoDB المفعّل الخاص بك
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://kederssllam_db_user:NqF8c0FtSCARPcNC@cluster0.hqhlnt6.mongodb.net/?appName=Cluster0")

# الإعدادات الرسمية لقنواتك لضمان الربط التلقائي
DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", -1003921766270))   # آيدي قناة المخزن الخاصة بك
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "MBC2_MOVIE")    # معرف قناة الاشتراك الإجباري
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))                           # آيدي حسابك الإداري (اختياري)
