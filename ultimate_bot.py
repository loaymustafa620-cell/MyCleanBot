import os
import sqlite3
import time
import threading
from datetime import datetime, timedelta
import telebot
from telebot import types

# ================================================================= #
# 1. CONFIGURATION & CREDENTIALS                                      #
# ================================================================= #

TOKEN = "8818180955:AAF7U-_msmDchmf-_s7rK_5gEPcLKICkfZw"
bot = telebot.TeleBot(TOKEN)

DEVELOPER_ID   = 6320384889
DEVELOPER_USER = "@X_16_LO_18_X"

DEFAULT_CHANNEL_ID   = -1003989835079
DEFAULT_CHANNEL_LINK = "https://t.me/X_F9_10_X"

# نقاط مكافأة الدعوة
REFERRAL_POINTS = 5

# ================================================================= #
# الـ 6 مواقع النشطة                                                 #
# ================================================================= #
LINKS_CONFIG = {
    "site_cuts_url": {"url": "https://cuts-url.com/M2qLN8A",    "code": "2007", "points": 1,
        "label_ar": "🎯 مهمة موقع Cuts-url (+1 نقطة)",         "label_en": "🎯 Cuts-url Task (+1 Point)"},
    "site_fclc":     {"url": "https://fc-lc.xyz/wfhNM",         "code": "1618", "points": 1,
        "label_ar": "🔥 مهمة موقع FC.LC (+1 نقطة)",            "label_en": "🔥 FC.LC Task (+1 Point)"},
    "site_exe_io":   {"url": "https://exe.io/TNr1VY",           "code": "1013", "points": 1,
        "label_ar": "🚀 مهمة موقع Exe.io (+1 نقطة)",           "label_en": "🚀 Exe.io Task (+1 Point)"},
    "site_monetag":  {"url": "https://www.effectivecpmnetwork.com/jkv5mhb0r?key=d074fd6cddb1e7dfe30b9db1ad00e25d",
        "code": "5599", "points": 1,
        "label_ar": "⚡ مهمة رابط Monetag الذكي (+1 نقطة)",    "label_en": "⚡ Monetag Smartlink (+1 Point)"},
    "site_adsterra": {"url": "https://www.effectivecpmnetwork.com/jkv5mhb0r?key=d074fd6cddb1e7dfe30b9db1ad00e25d",
        "code": "8844", "points": 1,
        "label_ar": "💎 مهمة رابط Adsterra المطور (+1 نقطة)",  "label_en": "💎 Adsterra Task (+1 Point)"},
    "site_mylead":   {"url": "https://www.effectivecpmnetwork.com/jkv5mhb0r?key=mylead",
        "code": "9900", "points": 1,
        "label_ar": "🌟 مهمة عروض MyLead الحصرية (+1 نقطة)",  "label_en": "🌟 MyLead Exclusive Task (+1 Point)"}
}

DEFAULT_REWARDS = {
    "balance_10": {"points": 38,  "title_ar": "شحن 10 جنيه رصيد / كاش",           "title_en": "Recharge 10 EGP Cash/Balance"},
    "balance_20": {"points": 76,  "title_ar": "شحن 20 جنيه رصيد / كاش",           "title_en": "Recharge 20 EGP Cash/Balance"},
    "balance_50": {"points": 190, "title_ar": "شحن 50 جنيه رصيد / كاش",           "title_en": "Recharge 50 EGP Cash/Balance"},
    "pubg_60":    {"points": 160, "title_ar": "شحن 60 شدة ببجي موبايل (PUBG)",     "title_en": "60 UC PUBG Mobile"},
    "ff_60":      {"points": 140, "title_ar": "شحن 60 جوهرة فري فاير (Free Fire)", "title_en": "60 Diamonds Free Fire"}
}

# ================================================================= #
# 2. TEXTS — ثنائي اللغة                                             #
# ================================================================= #

TEXTS = {
    "ar": {
        "choose_lang":      "🌐 اختر لغتك / Choose your language:",
        "welcome":          "🙋‍♂️ **أهلاً بك يا {name} في بوت الخدمات المتكامل!**\nقم بتنفيذ المهمات لتجميع النقاط وشحن الألعاب والرصيد مجاناً.",
        "sub_required":     "⚠️ **عذراً يا {name}! يجب الاشتراك في قناة البوت أولاً.**\n👇 اشترك ثم اضغط تأكيد:",
        "sub_confirmed":    "✅ تم تأكيد الاشتراك بنجاح!",
        "sub_failed":       "❌ أنت غير مشترك في القناة!",
        "activated":        "🎉 تم تفعيل حسابك! استخدم القائمة.",
        "banned":           "🚫 حسابك موقوف من استخدام البوت.",
        "btn_tasks":        "📋 مهمات",
        "btn_account":      "👤 الحساب",
        "btn_games":        "🎮 شحن ألعاب",
        "btn_balance":      "📱 شحن رصيد",
        "btn_referral":     "👥 دعوة الأصدقاء",
        "btn_lang":         "🌐 تغيير اللغة",
        "tasks_intro":
            "📋 **كيف تجمع النقاط؟ — اقرأ بعناية:**\n\n"
            "1️⃣ اضغط على أحد الروابط الـ 6 أدناه.\n"
            "2️⃣ سيفتح المتصفح — تخطَّ الإعلانات وانتظر العداد حتى النهاية.\n"
            "3️⃣ في **الصفحة الأخيرة** سيظهر لك **كود سري من 4 أرقام** (مثال: 2007).\n"
            "4️⃣ انسخ الكود وأرسله هنا في الشات مباشرة.\n"
            "💡 كل مهمة مرة واحدة كل 24 ساعة.\n\n"
            "👇 **الروابط النشطة الآن:**",
        "account_info":
            "👤 **معلومات حسابك:**\n\n"
            "📝 الاسم: {name}\n"
            "🆔 الآيدي: `{uid}`\n"
            "💎 رصيدك: *{pts}* نقطة\n"
            "👥 عدد من دعوتهم: *{refs}* شخص",
        "games_title":      "🎮 **اختر العرض المراد شحنه:**",
        "balance_title":    "📱 **اختر فئة شحن الرصيد:**",
        "code_cooldown":    "❌ قمت بهذه المهمة مسبقاً اليوم.\n⏳ انتظر: `{t}`",
        "code_success":
            "🎉 **تهانينا يا {name}! الكود صحيح.**\n"
            "✅ تمت إضافة *+{pts}* نقطة.\n"
            "💎 إجمالي رصيدك: *{total}* نقطة.",
        "code_wrong":       "⚠️ الكود غير صحيح! تأكد من نسخ الكود الرباعي الظاهر في نهاية الرابط.",
        "not_enough_pts":   "❌ نقاطك غير كافية! تحتاج {need} نقطة، لديك {have}.",
        "claim_registered": "✅ تم تسجيل الطلب!",
        "claim_ask_data":
            "📝 **طلبت: {title}**\n\n"
            "اكتب في رسالة واحدة:\n"
            "• آيدي اللعبة (لو شحن ألعاب) **أو** رقم الهاتف (لو شحن رصيد)\n"
            "• اسمك الكامل\n\n"
            "👇 أرسل البيانات الآن:",
        "claim_sent":       "✅ **تم إرسال طلبك للإدارة بنجاح!**\nسيتم تلبية طلبك قريباً.",
        "referral_msg":
            "👥 **نظام الدعوة:**\n\n"
            "📌 رابط دعوتك الخاص:\n`{link}`\n\n"
            "🎁 تحصل على *{rpts}* نقاط مجاناً عن كل صديق يسجل عبر رابطك!\n"
            "👥 عدد من دعوتهم حتى الآن: *{count}* شخص\n"
            "💎 نقاط كسبتها من الدعوات: *{earned}* نقطة",
        "referral_self":    "❌ لا يمكنك دعوة نفسك!",
        "referral_already": "ℹ️ أنت مسجل مسبقاً ولا تحتاج رابط دعوة.",
        "referral_bonus":
            "🎉 **مبروك يا {name}!**\n"
            "تم تسجيلك عبر رابط دعوة وحصلت على *+{pts}* نقاط هدية!\n"
            "💎 رصيدك الآن: *{total}* نقطة.",
        "referrer_bonus":
            "🔔 **مبروك!** انضم صديق جديد عبر رابطك.\n"
            "💎 تمت إضافة *+{pts}* نقطة لحسابك!\n"
            "👥 إجمالي دعواتك: *{count}*",
    },
    "en": {
        "choose_lang":      "🌐 Choose your language / اختر لغتك:",
        "welcome":          "🙋‍♂️ **Welcome {name} to the Ultimate Bot!**\nComplete tasks to earn points and get free game & balance top-ups.",
        "sub_required":     "⚠️ **Sorry {name}! You must join our channel first.**\n👇 Join then confirm:",
        "sub_confirmed":    "✅ Subscription confirmed!",
        "sub_failed":       "❌ You are not subscribed to the channel!",
        "activated":        "🎉 Account activated! Use the menu below.",
        "banned":           "🚫 Your account has been suspended.",
        "btn_tasks":        "📋 Tasks",
        "btn_account":      "👤 Account",
        "btn_games":        "🎮 Game Top-Up",
        "btn_balance":      "📱 Balance Top-Up",
        "btn_referral":     "👥 Invite Friends",
        "btn_lang":         "🌐 Change Language",
        "tasks_intro":
            "📋 **How to earn points — read carefully:**\n\n"
            "1️⃣ Tap any of the 6 links below.\n"
            "2️⃣ Your browser opens — skip the ads and wait for the timer.\n"
            "3️⃣ On the **last page** you will see a **4-digit secret code** (e.g. 2007).\n"
            "4️⃣ Copy the code and send it here in the chat.\n"
            "💡 Each task can be done once every 24 hours.\n\n"
            "👇 **Active links:**",
        "account_info":
            "👤 **Your Account:**\n\n"
            "📝 Name: {name}\n"
            "🆔 ID: `{uid}`\n"
            "💎 Points: *{pts}*\n"
            "👥 Friends invited: *{refs}*",
        "games_title":      "🎮 **Choose a gaming reward:**",
        "balance_title":    "📱 **Choose a balance top-up:**",
        "code_cooldown":    "❌ You already did this task today.\n⏳ Wait: `{t}`",
        "code_success":
            "🎉 **Congrats {name}! Correct code.**\n"
            "✅ *+{pts}* point(s) added.\n"
            "💎 Total balance: *{total}* points.",
        "code_wrong":       "⚠️ Wrong code! Make sure you copy the 4-digit code shown at the end of the link.",
        "not_enough_pts":   "❌ Not enough points! You need {need}, you have {have}.",
        "claim_registered": "✅ Request registered!",
        "claim_ask_data":
            "📝 **You requested: {title}**\n\n"
            "Send in one message:\n"
            "• Game ID (for game top-up) **or** phone number (for balance)\n"
            "• Your full name\n\n"
            "👇 Send details now:",
        "claim_sent":       "✅ **Your request was sent to admin!**\nIt will be fulfilled shortly.",
        "referral_msg":
            "👥 **Referral System:**\n\n"
            "📌 Your referral link:\n`{link}`\n\n"
            "🎁 Earn *{rpts}* free points for every friend who registers via your link!\n"
            "👥 Friends invited so far: *{count}*\n"
            "💎 Points earned from referrals: *{earned}*",
        "referral_self":    "❌ You cannot invite yourself!",
        "referral_already": "ℹ️ You are already registered.",
        "referral_bonus":
            "🎉 **Congrats {name}!**\n"
            "You registered via a referral link and got *+{pts}* bonus points!\n"
            "💎 Your balance: *{total}* points.",
        "referrer_bonus":
            "🔔 **Great!** A new friend joined via your link.\n"
            "💎 *+{pts}* points added to your account!\n"
            "👥 Total referrals: *{count}*",
    }
}

def t(uid, key, **kwargs):
    """جلب النص بلغة المستخدم"""
    lang = get_user_lang(uid)
    text = TEXTS.get(lang, TEXTS["ar"]).get(key, key)
    return text.format(**kwargs) if kwargs else text

# ================================================================= #
# 3. DATABASE                                                         #
# ================================================================= #

DB_FILE = "ultimate_bot_storage.db"
db_lock = threading.Lock()

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    with db_lock:
        conn = get_connection()
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY,
            username      TEXT,
            first_name    TEXT,
            points        INTEGER DEFAULT 0,
            is_banned     INTEGER DEFAULT 0,
            lang          TEXT DEFAULT 'ar',
            referred_by   INTEGER DEFAULT NULL,
            referral_count INTEGER DEFAULT 0,
            referral_pts  INTEGER DEFAULT 0,
            joined_at     TEXT DEFAULT (datetime('now'))
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS task_logs (
            user_id         INTEGER,
            task_key        TEXT,
            completion_time TEXT,
            PRIMARY KEY (user_id, task_key)
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS rewards (
            reward_key TEXT PRIMARY KEY,
            points     INTEGER,
            title_ar   TEXT,
            title_en   TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS charge_requests (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            reward_key TEXT,
            user_data  TEXT,
            status     TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now'))
        )''')

        c.execute('SELECT COUNT(*) FROM rewards')
        if c.fetchone()[0] == 0:
            for key, info in DEFAULT_REWARDS.items():
                c.execute('INSERT INTO rewards VALUES (?,?,?,?)',
                          (key, info["points"], info["title_ar"], info["title_en"]))

        c.execute('INSERT OR IGNORE INTO settings VALUES (?,?)', ('channel_id',   str(DEFAULT_CHANNEL_ID)))
        c.execute('INSERT OR IGNORE INTO settings VALUES (?,?)', ('channel_link', DEFAULT_CHANNEL_LINK))

        conn.commit()
        conn.close()

# ── DB helpers ───────────────────────────────────────────────────── #

def get_setting(key):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT value FROM settings WHERE key=?', (key,))
        row = c.fetchone()
        conn.close()
    return row[0] if row else None

def set_setting(key, value):
    with db_lock:
        conn = get_connection()
        conn.execute('INSERT OR REPLACE INTO settings VALUES (?,?)', (key, str(value)))
        conn.commit()
        conn.close()

def get_channel_id():
    val = get_setting('channel_id')
    return int(val) if val else DEFAULT_CHANNEL_ID

def get_channel_link():
    return get_setting('channel_link') or DEFAULT_CHANNEL_LINK

def user_exists(user_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT 1 FROM users WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
    return row is not None

def add_user_if_not_exists(user_id, username, first_name, referred_by=None):
    """يضيف المستخدم ويرجع True لو كان جديداً"""
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT 1 FROM users WHERE user_id=?', (user_id,))
        if c.fetchone():
            conn.close()
            return False   # موجود مسبقاً
        c.execute(
            'INSERT INTO users (user_id, username, first_name, points, referred_by) VALUES (?,?,?,0,?)',
            (user_id, username or "None", first_name or "User", referred_by))
        conn.commit()
        conn.close()
    return True   # جديد

def get_user_lang(user_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT lang FROM users WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
    return row[0] if row else 'ar'

def set_user_lang(user_id, lang):
    with db_lock:
        conn = get_connection()
        conn.execute('UPDATE users SET lang=? WHERE user_id=?', (lang, user_id))
        conn.commit()
        conn.close()

def get_user_points(user_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT points FROM users WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
    return row[0] if row else 0

def update_user_points(user_id, delta):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        if delta < 0:
            c.execute('UPDATE users SET points = MAX(0, points + ?) WHERE user_id=?', (delta, user_id))
        else:
            c.execute('UPDATE users SET points = points + ? WHERE user_id=?', (delta, user_id))
        conn.commit()
        conn.close()

def get_user_info(user_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id, username, first_name, points, is_banned, lang, referred_by, referral_count, referral_pts, joined_at FROM users WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
    return row

def get_total_users_count():
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM users')
        row = c.fetchone()
        conn.close()
    return row[0] if row else 0

def get_all_user_ids():
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id FROM users WHERE is_banned=0')
        rows = c.fetchall()
        conn.close()
    return [r[0] for r in rows]

def ban_user(user_id):
    with db_lock:
        conn = get_connection()
        conn.execute('UPDATE users SET is_banned=1 WHERE user_id=?', (user_id,))
        conn.commit()
        conn.close()

def unban_user(user_id):
    with db_lock:
        conn = get_connection()
        conn.execute('UPDATE users SET is_banned=0 WHERE user_id=?', (user_id,))
        conn.commit()
        conn.close()

def is_user_banned(user_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT is_banned FROM users WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
    return bool(row and row[0])

def add_referral_to_referrer(referrer_id):
    """يزيد عداد الدعوات ونقاط الدعوة للشخص الداعي"""
    with db_lock:
        conn = get_connection()
        conn.execute(
            'UPDATE users SET referral_count = referral_count+1, referral_pts = referral_pts+?, points = points+? WHERE user_id=?',
            (REFERRAL_POINTS, REFERRAL_POINTS, referrer_id))
        conn.commit()
        conn.close()

def get_referral_info(user_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT referral_count, referral_pts FROM users WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
    return (row[0], row[1]) if row else (0, 0)

def check_task_cooldown(user_id, task_key):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT completion_time FROM task_logs WHERE user_id=? AND task_key=?', (user_id, task_key))
        row = c.fetchone()
        conn.close()
    if row:
        last_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        if datetime.now() < last_time + timedelta(hours=24):
            remaining = (last_time + timedelta(hours=24)) - datetime.now()
            h, rem = divmod(int(remaining.total_seconds()), 3600)
            m = rem // 60
            return False, f"{h}h {m}m"
    return True, "OK"

def save_task_completion(user_id, task_key):
    with db_lock:
        conn = get_connection()
        conn.execute(
            'INSERT OR REPLACE INTO task_logs (user_id, task_key, completion_time) VALUES (?,?,?)',
            (user_id, task_key, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

def load_rewards_from_db():
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT reward_key, points, title_ar, title_en FROM rewards')
        rows = c.fetchall()
        conn.close()
    return {r[0]: {"points": r[1], "title_ar": r[2], "title_en": r[3]} for r in rows}

def update_reward_price_in_db(reward_key, new_points):
    with db_lock:
        conn = get_connection()
        conn.execute('UPDATE rewards SET points=? WHERE reward_key=?', (new_points, reward_key))
        conn.commit()
        conn.close()

def save_charge_request(user_id, reward_key, user_data):
    with db_lock:
        conn = get_connection()
        conn.execute('INSERT INTO charge_requests (user_id, reward_key, user_data) VALUES (?,?,?)',
                     (user_id, reward_key, user_data))
        conn.commit()
        conn.close()

def get_pending_requests():
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id, user_id, reward_key, user_data, created_at FROM charge_requests WHERE status="pending" ORDER BY id DESC LIMIT 20')
        rows = c.fetchall()
        conn.close()
    return rows

def update_request_status(req_id, status):
    with db_lock:
        conn = get_connection()
        conn.execute('UPDATE charge_requests SET status=? WHERE id=?', (status, req_id))
        conn.commit()
        conn.close()

# ================================================================= #
# 4. SUBSCRIPTION CHECK                                               #
# ================================================================= #

def check_forced_subscription(user_id):
    if user_id == DEVELOPER_ID:
        return True
    try:
        member = bot.get_chat_member(get_channel_id(), user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return True

# ================================================================= #
# 5. KEYBOARDS                                                        #
# ================================================================= #

def get_lang_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇸🇦 العربية", callback_data="setlang_ar"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en")
    )
    return markup

def get_main_keyboard(uid):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton(t(uid, "btn_tasks")),
        types.KeyboardButton(t(uid, "btn_account")),
        types.KeyboardButton(t(uid, "btn_games")),
        types.KeyboardButton(t(uid, "btn_balance")),
        types.KeyboardButton(t(uid, "btn_referral")),
        types.KeyboardButton(t(uid, "btn_lang"))
    )
    return markup

def get_subscription_keyboard(uid):
    lang = get_user_lang(uid)
    join_text = "📢 اشترك في القناة" if lang == "ar" else "📢 Join Channel"
    confirm_text = "🔄 تأكيد الاشتراك" if lang == "ar" else "🔄 Confirm Subscription"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(join_text,    url=get_channel_link()),
        types.InlineKeyboardButton(confirm_text, callback_data="check_sub")
    )
    return markup

def get_tasks_inline_keyboard(uid):
    lang = get_user_lang(uid)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for key, info in LINKS_CONFIG.items():
        label = info["label_ar"] if lang == "ar" else info["label_en"]
        markup.add(types.InlineKeyboardButton(label, url=info["url"]))
    return markup

def get_rewards_keyboard(uid, reward_type):
    lang = get_user_lang(uid)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for key, info in load_rewards_from_db().items():
        show = (reward_type == "games" and ("pubg" in key or "ff" in key)) or \
               (reward_type == "balance" and "balance" in key)
        if show:
            title = info["title_ar"] if lang == "ar" else info["title_en"]
            markup.add(types.InlineKeyboardButton(
                f"🎁 {title} ({info['points']} P)", callback_data=f"claim_{key}"))
    return markup

# ================================================================= #
# 6. GUARD                                                            #
# ================================================================= #

def guard(message):
    uid = message.from_user.id
    if is_user_banned(uid):
        bot.send_message(message.chat.id, t(uid, "banned"))
        return False
    if not check_forced_subscription(uid):
        bot.send_message(message.chat.id,
            t(uid, "sub_required", name=message.from_user.first_name or "User"),
            reply_markup=get_subscription_keyboard(uid), parse_mode="Markdown")
        return False
    return True

# ================================================================= #
# 7. /start — مع دعم رابط الدعوة                                     #
# ================================================================= #

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid   = message.from_user.id
    uname = message.from_user.username or "None"
    fname = message.from_user.first_name or "User"

    # استخراج الـ referral_id من الرابط لو موجود (?start=ref_XXXX)
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id == uid:
                referrer_id = None  # لا تدعو نفسك
        except ValueError:
            referrer_id = None

    is_new = add_user_if_not_exists(uid, uname, fname, referred_by=referrer_id)

    if is_user_banned(uid):
        bot.send_message(message.chat.id, t(uid, "banned"))
        return

    # لو جديد وجاء عبر دعوة — أعطه نقاط وأعطِ الداعي نقاط
    if is_new and referrer_id and user_exists(referrer_id):
        # نقاط للمستخدم الجديد
        update_user_points(uid, REFERRAL_POINTS)
        new_total = get_user_points(uid)
        # نقاط للداعي
        add_referral_to_referrer(referrer_id)
        ref_count, _ = get_referral_info(referrer_id)
        # إشعار للمستخدم الجديد
        try:
            bot.send_message(uid,
                t(uid, "referral_bonus", name=fname, pts=REFERRAL_POINTS, total=new_total),
                parse_mode="Markdown")
        except Exception:
            pass
        # إشعار للداعي
        try:
            bot.send_message(referrer_id,
                t(referrer_id, "referrer_bonus", pts=REFERRAL_POINTS, count=ref_count),
                parse_mode="Markdown")
        except Exception:
            pass

    # لو المستخدم جديد تماماً → اسأله اللغة
    if is_new:
        bot.send_message(message.chat.id,
            TEXTS["ar"]["choose_lang"] + "\n" + TEXTS["en"]["choose_lang"],
            reply_markup=get_lang_keyboard())
        return

    # مستخدم موجود → تحقق من الاشتراك وافتح القائمة
    if not check_forced_subscription(uid):
        bot.send_message(message.chat.id,
            t(uid, "sub_required", name=fname),
            reply_markup=get_subscription_keyboard(uid), parse_mode="Markdown")
        return

    bot.send_message(message.chat.id,
        t(uid, "welcome", name=fname),
        reply_markup=get_main_keyboard(uid), parse_mode="Markdown")

# ── اختيار اللغة ─────────────────────────────────────────────────── #

@bot.callback_query_handler(func=lambda c: c.data.startswith("setlang_"))
def handle_set_lang(call):
    uid  = call.from_user.id
    lang = call.data.replace("setlang_", "")
    set_user_lang(uid, lang)
    bot.answer_callback_query(call.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass

    fname = call.from_user.first_name or "User"

    if not check_forced_subscription(uid):
        bot.send_message(call.message.chat.id,
            t(uid, "sub_required", name=fname),
            reply_markup=get_subscription_keyboard(uid), parse_mode="Markdown")
        return

    bot.send_message(call.message.chat.id,
        t(uid, "welcome", name=fname),
        reply_markup=get_main_keyboard(uid), parse_mode="Markdown")

# ── تأكيد الاشتراك ───────────────────────────────────────────────── #

@bot.callback_query_handler(func=lambda c: c.data == "check_sub")
def handle_check_sub(call):
    uid = call.from_user.id
    if check_forced_subscription(uid):
        bot.answer_callback_query(call.id, t(uid, "sub_confirmed"), show_alert=True)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        bot.send_message(call.message.chat.id, t(uid, "activated"),
                         reply_markup=get_main_keyboard(uid))
    else:
        bot.answer_callback_query(call.id, t(uid, "sub_failed"), show_alert=True)

# ================================================================= #
# 8. MAIN USER HANDLER                                                #
# ================================================================= #

@bot.message_handler(func=lambda m: True)
def handle_user_actions(message):
    uid   = message.from_user.id
    fname = message.from_user.first_name or "User"
    uname = message.from_user.username or "None"
    add_user_if_not_exists(uid, uname, fname)

    # أوامر الأدمن بدون guard
    if message.text == "/admin" and uid == DEVELOPER_ID:
        show_admin_panel(message.chat.id)
        return

    if not guard(message):
        return

    text = message.text
    lang = get_user_lang(uid)

    # ── زر تغيير اللغة ───────────────────────────────────────────── #
    if text in (TEXTS["ar"]["btn_lang"], TEXTS["en"]["btn_lang"]):
        bot.send_message(message.chat.id,
            TEXTS["ar"]["choose_lang"] + "\n" + TEXTS["en"]["choose_lang"],
            reply_markup=get_lang_keyboard())

    # ── المهمات ──────────────────────────────────────────────────── #
    elif text in (TEXTS["ar"]["btn_tasks"], TEXTS["en"]["btn_tasks"]):
        bot.send_message(message.chat.id,
            t(uid, "tasks_intro"),
            reply_markup=get_tasks_inline_keyboard(uid), parse_mode="Markdown")

    # ── الحساب ───────────────────────────────────────────────────── #
    elif text in (TEXTS["ar"]["btn_account"], TEXTS["en"]["btn_account"]):
        pts = get_user_points(uid)
        refs, _ = get_referral_info(uid)
        bot.send_message(message.chat.id,
            t(uid, "account_info", name=fname, uid=uid, pts=pts, refs=refs),
            parse_mode="Markdown")

    # ── شحن ألعاب ────────────────────────────────────────────────── #
    elif text in (TEXTS["ar"]["btn_games"], TEXTS["en"]["btn_games"]):
        bot.send_message(message.chat.id,
            t(uid, "games_title"),
            reply_markup=get_rewards_keyboard(uid, "games"))

    # ── شحن رصيد ─────────────────────────────────────────────────── #
    elif text in (TEXTS["ar"]["btn_balance"], TEXTS["en"]["btn_balance"]):
        bot.send_message(message.chat.id,
            t(uid, "balance_title"),
            reply_markup=get_rewards_keyboard(uid, "balance"))

    # ── الدعوة ───────────────────────────────────────────────────── #
    elif text in (TEXTS["ar"]["btn_referral"], TEXTS["en"]["btn_referral"]):
        ref_link = f"https://t.me/{bot.get_me().username}?start=ref_{uid}"
        count, earned = get_referral_info(uid)
        bot.send_message(message.chat.id,
            t(uid, "referral_msg", link=ref_link, rpts=REFERRAL_POINTS, count=count, earned=earned),
            parse_mode="Markdown")

    # ── فحص الأكواد ──────────────────────────────────────────────── #
    else:
        code_matched = False
        for task_key, info in LINKS_CONFIG.items():
            if text == info["code"]:
                code_matched = True
                allowed, wait_time = check_task_cooldown(uid, task_key)
                if not allowed:
                    bot.send_message(message.chat.id,
                        t(uid, "code_cooldown", t=wait_time), parse_mode="Markdown")
                else:
                    update_user_points(uid, info["points"])
                    save_task_completion(uid, task_key)
                    total = get_user_points(uid)
                    bot.send_message(message.chat.id,
                        t(uid, "code_success", name=fname, pts=info["points"], total=total),
                        parse_mode="Markdown")
                break

        if not code_matched:
            bot.send_message(message.chat.id, t(uid, "code_wrong"))

# ================================================================= #
# 9. REWARDS CLAIM                                                    #
# ================================================================= #

@bot.callback_query_handler(func=lambda c: c.data.startswith("claim_"))
def handle_claim_rewards(call):
    uid        = call.from_user.id
    reward_key = call.data.replace("claim_", "")
    rewards    = load_rewards_from_db()

    if reward_key not in rewards:
        return

    info     = rewards[reward_key]
    user_pts = get_user_points(uid)
    lang     = get_user_lang(uid)

    if user_pts < info["points"]:
        bot.answer_callback_query(call.id,
            t(uid, "not_enough_pts", need=info["points"], have=user_pts), show_alert=True)
        return

    update_user_points(uid, -info["points"])
    bot.answer_callback_query(call.id, t(uid, "claim_registered"), show_alert=True)

    title = info["title_ar"] if lang == "ar" else info["title_en"]
    msg = bot.send_message(call.message.chat.id,
        t(uid, "claim_ask_data", title=title), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_user_delivery_data, reward_key, info["points"])

def process_user_delivery_data(message, reward_key, points_cost):
    uid        = message.from_user.id
    user_input = message.text or "(لا يوجد نص)"
    rewards    = load_rewards_from_db()
    reward_info = rewards.get(reward_key, {})

    save_charge_request(uid, reward_key, user_input)

    admin_alert = (
        f"🚨 **طلب شحن جديد!**\n\n"
        f"👤 الاسم: {message.from_user.first_name}\n"
        f"🆔 الآيدي: `{uid}`\n"
        f"📦 الطلب: *{reward_info.get('title_ar','؟')}*\n"
        f"💎 النقاط المخصومة: {points_cost}\n"
        f"📌 **بيانات الشحن:** `{user_input}`"
    )
    try:
        bot.send_message(DEVELOPER_ID, admin_alert, parse_mode="Markdown")
    except Exception as e:
        print(f"[ERROR] فشل إرسال تنبيه الأدمن: {e}")

    bot.send_message(message.chat.id,
        t(uid, "claim_sent"), reply_markup=get_main_keyboard(uid))

# ================================================================= #
# 10. ADMIN PANEL                                                     #
# ================================================================= #

def show_admin_panel(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("⚙️ تعديل أسعار المكافآت",         callback_data="adm_change_prices"),
        types.InlineKeyboardButton("📺 تعديل بيانات القناة الإجبارية", callback_data="adm_change_channel"),
        types.InlineKeyboardButton("📊 إحصائيات البوت",                callback_data="adm_stats"),
        types.InlineKeyboardButton("📋 الطلبات المعلقة",                callback_data="adm_pending"),
        types.InlineKeyboardButton("🔍 البحث عن مستخدم",                callback_data="adm_search_user"),
        types.InlineKeyboardButton("➕ إضافة نقاط لمستخدم",             callback_data="adm_add_points"),
        types.InlineKeyboardButton("➖ خصم نقاط من مستخدم",             callback_data="adm_remove_points"),
        types.InlineKeyboardButton("🚫 حظر مستخدم",                     callback_data="adm_ban_user"),
        types.InlineKeyboardButton("✅ رفع حظر مستخدم",                  callback_data="adm_unban_user"),
        types.InlineKeyboardButton("📤 إرسال إثبات شحن لعميل",          callback_data="adm_send_proof"),
        types.InlineKeyboardButton("📢 إذاعة جماعية (Broadcast)",       callback_data="adm_broadcast"),
    )
    bot.send_message(chat_id, "👑 **لوحة تحكم الإدارة الكاملة:**",
                     reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("adm_"))
def handle_admin_callbacks(call):
    if call.from_user.id != DEVELOPER_ID:
        bot.answer_callback_query(call.id, "🚫 ليس لديك صلاحية!", show_alert=True)
        return

    action = call.data
    bot.answer_callback_query(call.id)

    if action == "adm_stats":
        total = get_total_users_count()
        bot.send_message(call.message.chat.id,
            f"📊 **إحصائيات البوت:**\n\n👥 إجمالي المستخدمين: *{total}*",
            parse_mode="Markdown")

    elif action == "adm_pending":
        requests = get_pending_requests()
        if not requests:
            bot.send_message(call.message.chat.id, "✅ لا توجد طلبات معلقة حالياً.")
            return
        rewards = load_rewards_from_db()
        for req in requests:
            req_id, user_id, reward_key, user_data, created_at = req
            title = rewards.get(reward_key, {}).get('title_ar', reward_key)
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("✅ تم التنفيذ", callback_data=f"req_done_{req_id}_{user_id}"),
                types.InlineKeyboardButton("❌ رفض",        callback_data=f"req_reject_{req_id}_{user_id}")
            )
            bot.send_message(call.message.chat.id,
                f"🔔 **طلب #{req_id}**\n"
                f"👤 آيدي العميل: `{user_id}`\n"
                f"📦 الطلب: {title}\n"
                f"📌 البيانات: `{user_data}`\n"
                f"🕐 التاريخ: {created_at}",
                reply_markup=markup, parse_mode="Markdown")

    elif action == "adm_change_prices":
        rewards = load_rewards_from_db()
        markup  = types.InlineKeyboardMarkup(row_width=1)
        for key, info in rewards.items():
            markup.add(types.InlineKeyboardButton(
                f"✏️ {info['title_ar']} ({info['points']} P)",
                callback_data=f"editprice_{key}"))
        bot.send_message(call.message.chat.id,
            "🎯 اختر المكافأة لتعديل سعرها:", reply_markup=markup)

    elif action == "adm_change_channel":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔢 تغيير Channel ID",   callback_data="adm_ch_id"),
            types.InlineKeyboardButton("🔗 تغيير Channel Link", callback_data="adm_ch_link"),
        )
        cid   = get_channel_id()
        clink = get_channel_link()
        bot.send_message(call.message.chat.id,
            f"📺 **بيانات القناة الحالية:**\n🆔 ID: `{cid}`\n🔗 Link: {clink}\n\nاختر ما تريد تعديله:",
            reply_markup=markup, parse_mode="Markdown")

    elif action == "adm_ch_id":
        msg = bot.send_message(call.message.chat.id,
            "🔢 أرسل الـ Channel ID الجديد (مثال: -1001234567890):")
        bot.register_next_step_handler(msg, admin_save_channel_id)

    elif action == "adm_ch_link":
        msg = bot.send_message(call.message.chat.id,
            "🔗 أرسل رابط القناة الجديد (مثال: https://t.me/mychannel):")
        bot.register_next_step_handler(msg, admin_save_channel_link)

    elif action == "adm_search_user":
        msg = bot.send_message(call.message.chat.id, "🔍 أرسل آيدي المستخدم الرقمي:")
        bot.register_next_step_handler(msg, admin_search_user)

    elif action == "adm_add_points":
        msg = bot.send_message(call.message.chat.id,
            "➕ أرسل: <آيدي> <نقاط>\nمثال: 123456789 50")
        bot.register_next_step_handler(msg, admin_add_points_handler)

    elif action == "adm_remove_points":
        msg = bot.send_message(call.message.chat.id,
            "➖ أرسل: <آيدي> <نقاط>\nمثال: 123456789 20")
        bot.register_next_step_handler(msg, admin_remove_points_handler)

    elif action == "adm_ban_user":
        msg = bot.send_message(call.message.chat.id, "🚫 أرسل آيدي المستخدم:")
        bot.register_next_step_handler(msg, admin_ban_user_handler)

    elif action == "adm_unban_user":
        msg = bot.send_message(call.message.chat.id, "✅ أرسل آيدي المستخدم:")
        bot.register_next_step_handler(msg, admin_unban_user_handler)

    elif action == "adm_send_proof":
        msg = bot.send_message(call.message.chat.id, "👤 أرسل آيدي المستخدم:")
        bot.register_next_step_handler(msg, admin_get_user_id_for_proof)

    elif action == "adm_broadcast":
        msg = bot.send_message(call.message.chat.id, "📢 أرسل نص الرسالة الإذاعية:")
        bot.register_next_step_handler(msg, admin_execute_broadcast)

# ── أزرار الطلبات ─────────────────────────────────────────────────── #

@bot.callback_query_handler(func=lambda c: c.data.startswith("req_done_") or c.data.startswith("req_reject_"))
def handle_request_action(call):
    if call.from_user.id != DEVELOPER_ID:
        return
    parts   = call.data.split("_")
    status  = "done" if "done" in call.data else "rejected"
    req_id  = int(parts[2])
    user_id = int(parts[3])
    update_request_status(req_id, status)
    bot.answer_callback_query(call.id, "✅ تم تحديث الطلب")
    if status == "done":
        try:
            bot.send_message(user_id, "🎉 **تهانينا! تم تنفيذ طلب الشحن بنجاح من قبل الإدارة.**",
                             parse_mode="Markdown")
        except Exception:
            pass
        bot.send_message(call.message.chat.id, f"✅ الطلب #{req_id} تم تنفيذه.")
    else:
        try:
            bot.send_message(user_id, "❌ **عذراً، تم رفض طلبك. تواصل مع الدعم.**",
                             parse_mode="Markdown")
        except Exception:
            pass
        bot.send_message(call.message.chat.id, f"❌ الطلب #{req_id} تم رفضه.")

# ── تعديل سعر ────────────────────────────────────────────────────── #

@bot.callback_query_handler(func=lambda c: c.data.startswith("editprice_"))
def handle_edit_price_selection(call):
    if call.from_user.id != DEVELOPER_ID:
        return
    reward_key = call.data.replace("editprice_", "")
    bot.answer_callback_query(call.id)
    rewards = load_rewards_from_db()
    info    = rewards.get(reward_key, {})
    msg = bot.send_message(call.message.chat.id,
        f"🔢 **المكافأة:** {info.get('title_ar','؟')}\n"
        f"💰 **السعر الحالي:** {info.get('points','؟')} نقطة\n\n"
        "📥 أرسل السعر الجديد (رقم فقط):")
    bot.register_next_step_handler(msg, admin_save_new_price, reward_key)

def admin_save_new_price(message, reward_key):
    try:
        new_points = int(message.text.strip())
        if new_points < 0:
            bot.send_message(message.chat.id, "❌ لا يمكن وضع سعر سالب.")
            return
        update_reward_price_in_db(reward_key, new_points)
        rewards = load_rewards_from_db()
        info    = rewards.get(reward_key, {})
        bot.send_message(message.chat.id,
            f"✅ **تم التحديث!**\nالسعر الجديد لـ *{info.get('title_ar','؟')}*: **{new_points}** نقطة.",
            parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل رقماً صحيحاً فقط.")

# ── تعديل القناة ─────────────────────────────────────────────────── #

def admin_save_channel_id(message):
    try:
        new_id = int(message.text.strip())
        set_setting('channel_id', new_id)
        bot.send_message(message.chat.id, f"✅ تم حفظ Channel ID الجديد: `{new_id}`", parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "❌ يجب إرسال رقم صحيح.")

def admin_save_channel_link(message):
    new_link = message.text.strip()
    if not new_link.startswith("https://"):
        bot.send_message(message.chat.id, "❌ الرابط يجب أن يبدأ بـ https://")
        return
    set_setting('channel_link', new_link)
    bot.send_message(message.chat.id, f"✅ تم حفظ رابط القناة: {new_link}")

# ── بحث عن مستخدم ────────────────────────────────────────────────── #

def admin_search_user(message):
    try:
        target_id = int(message.text.strip())
        info = get_user_info(target_id)
        if not info:
            bot.send_message(message.chat.id, "❌ المستخدم غير موجود.")
            return
        uid, uname, fname, pts, banned, lang, ref_by, ref_count, ref_pts, joined = info
        bot.send_message(message.chat.id,
            f"👤 **معلومات المستخدم:**\n\n"
            f"🆔 الآيدي: `{uid}`\n"
            f"📝 الاسم: {fname}\n"
            f"👤 اليوزر: @{uname}\n"
            f"💎 النقاط: {pts}\n"
            f"🌐 اللغة: {lang}\n"
            f"👥 دعوات: {ref_count} (كسب {ref_pts} نقطة)\n"
            f"🚫 محظور: {'نعم' if banned else 'لا'}\n"
            f"📅 انضم: {joined}",
            parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل آيدي رقمي صحيح.")

# ── إضافة / خصم نقاط ─────────────────────────────────────────────── #

def admin_add_points_handler(message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            raise ValueError
        target_id = int(parts[0])
        pts       = int(parts[1])
        update_user_points(target_id, pts)
        new_pts = get_user_points(target_id)
        bot.send_message(message.chat.id,
            f"✅ تمت إضافة *{pts}* نقطة للمستخدم `{target_id}`.\n💎 رصيده: *{new_pts}*.",
            parse_mode="Markdown")
        try:
            bot.send_message(target_id,
                f"🎁 تمت إضافة *{pts}* نقطة لحسابك من الإدارة!\n💎 رصيدك الآن: *{new_pts}*.",
                parse_mode="Markdown")
        except Exception:
            pass
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "❌ الصيغة: <آيدي> <نقاط> — مثال: 123456 50")

def admin_remove_points_handler(message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            raise ValueError
        target_id = int(parts[0])
        pts       = int(parts[1])
        update_user_points(target_id, -pts)
        new_pts = get_user_points(target_id)
        bot.send_message(message.chat.id,
            f"✅ تم خصم *{pts}* نقطة من `{target_id}`.\n💎 رصيده: *{new_pts}*.",
            parse_mode="Markdown")
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "❌ الصيغة: <آيدي> <نقاط> — مثال: 123456 20")

# ── حظر / رفع حظر ────────────────────────────────────────────────── #

def admin_ban_user_handler(message):
    try:
        target_id = int(message.text.strip())
        ban_user(target_id)
        bot.send_message(message.chat.id, f"🚫 تم حظر `{target_id}` بنجاح.", parse_mode="Markdown")
        try:
            bot.send_message(target_id, "🚫 تم إيقاف حسابك من استخدام البوت.")
        except Exception:
            pass
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل آيدي رقمي صحيح.")

def admin_unban_user_handler(message):
    try:
        target_id = int(message.text.strip())
        unban_user(target_id)
        bot.send_message(message.chat.id, f"✅ تم رفع الحظر عن `{target_id}`.", parse_mode="Markdown")
        try:
            bot.send_message(target_id, "✅ تم رفع الحظر عن حسابك!")
        except Exception:
            pass
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل آيدي رقمي صحيح.")

# ── إثبات شحن ────────────────────────────────────────────────────── #

def admin_get_user_id_for_proof(message):
    try:
        target_id = int(message.text.strip())
        msg = bot.send_message(message.chat.id,
            f"📸 أرسل صورة إيصال الشحن للمستخدم `{target_id}`:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, admin_send_image_proof_to_user, target_id)
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل آيدي رقمي صحيح.")

def admin_send_image_proof_to_user(message, target_id):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌ يجب إرسال صورة.")
        return
    file_id = message.photo[-1].file_id
    try:
        bot.send_photo(target_id, file_id,
            caption="🎉 **تم شحن طلبك بنجاح!**\n📸 إليك إيصال الشحن الرسمي.",
            parse_mode="Markdown")
        bot.send_message(message.chat.id, f"✅ تم تسليم الإثبات للمستخدم `{target_id}`.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ فشل الإرسال: {e}")

# ── إذاعة جماعية ─────────────────────────────────────────────────── #

def admin_execute_broadcast(message):
    broadcast_text = message.text
    users = get_all_user_ids()
    bot.send_message(message.chat.id, f"🔄 جاري الإذاعة لـ {len(users)} مستخدم...")
    success = 0
    failed  = 0
    for uid in users:
        try:
            bot.send_message(uid, broadcast_text)
            success += 1
            time.sleep(0.05)
        except Exception:
            failed += 1
    bot.send_message(message.chat.id,
        f"✅ **اكتملت الإذاعة:**\n✔️ نجح: {success}\n❌ فشل: {failed}",
        parse_mode="Markdown")

# ================================================================= #
# 11. LAUNCH                                                          #
# ================================================================= #

if __name__ == "__main__":
    init_db()
    print("=" * 52)
    print("🤖 البوت يعمل الآن بنجاح...")
    print("⚙️ نظام الدعوة مفعل — نظام اللغتين مفعل.")
    print("=" * 52)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

