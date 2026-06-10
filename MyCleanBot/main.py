import os
import sqlite3
import time
import threading
from datetime import datetime, timedelta
from functools import partial
import telebot
from telebot import types

# ================================================================= #
# 1. CONFIGURATION                                                    #
# ================================================================
TOKEN ="8818180955:AAEbZgFRKFvNXDdeSvF0KQLnZW94DVDNvLI"
bot = telebot.TeleBot(TOKEN)

DEVELOPER_ID   = 6320384889
DEVELOPER_USER = "@X_16_LO_18_X"

DEFAULT_CHANNEL_ID   = -1003989835079
DEFAULT_CHANNEL_LINK = "https://t.me/X_F9_10_X"

REFERRAL_POINTS    = 5
MAX_REFERRALS_DAY  = 3   # حد أقصى للدعوات في اليوم

# ── إعدادات سحب الدولار ──────────────────────────────────────────── #
DOLLAR_RATE        = 50   # سعر الدولار بالجنيه
DOLLAR_FEE         = 10   # عمولة ثابتة بالجنيه لكل عملية سحب
WALLET_ADDRESS     = "YOUR_WALLET_ADDRESS_HERE"  # ← غيّر ده لعنوان محفظتك

# ================================================================= #
# 3. DEFAULT DATA                                                     #
# ================================================================= #

DEFAULT_LINKS = {
    "site_cuts_url":   {"url": "https://cuts-url.com/M2qLN8A",
        "code": "2007", "points": 1,
        "label_ar": "🎯 Cuts-url (+1 نقطة)",        "label_en": "🎯 Cuts-url (+1 Point)"},
    "site_fclc":       {"url": "https://fc-lc.xyz/wfhNM",
        "code": "1618", "points": 1,
        "label_ar": "🔥 FC.LC (+1 نقطة)",           "label_en": "🔥 FC.LC (+1 Point)"},
    "site_exe_io":     {"url": "https://exe.io/TNr1VY",
        "code": "1013", "points": 1,
        "label_ar": "🚀 Exe.io (+1 نقطة)",          "label_en": "🚀 Exe.io (+1 Point)"},
    "site_shrinkme":   {"url": "https://shrinkme.click/Y4iRmMN",
        "code": "5089", "points": 1,
        "label_ar": "🌟 ShrinkMe (+1 نقطة)",        "label_en": "🌟 ShrinkMe (+1 Point)"},
    "site_ouo_io":     {"url": "https://ouo.io/1ttPwT",
        "code": "1698", "points": 1,
        "label_ar": "🍀 Ouo.io (+1 نقطة)",          "label_en": "🍀 Ouo.io (+1 Point)"},
    "site_urlshortx":  {"url": "https://xpshort.com/qMPe",
        "code": "5566", "points": 1,
        "label_ar": "⚡ UrlShortx (+1 نقطة)",       "label_en": "⚡ UrlShortx (+1 Point)"},
    "site_gplinks":    {"url": "https://gplinks.co/QDeaVpV",
        "code": "5839", "points": 1,
        "label_ar": "📡 GPLinks (+1 نقطة)",         "label_en": "📡 GPLinks (+1 Point)"},
    "site_linktarget": {"url": "https://direct-link.net/6197933/OSqBS5wyHXrZ",
        "code": "7893", "points": 1,
        "label_ar": "🎪 Link-Target (+1 نقطة)",     "label_en": "🎪 Link-Target (+1 Point)"},
    "site_oiila":      {"url": "https://oii.la/savUEp0Za",
        "code": "0852", "points": 1,
        "label_ar": "🔮 Oii.la (+1 نقطة)",          "label_en": "🔮 Oii.la (+1 Point)"},
    "site_tpili":      {"url": "https://tpi.li/1LL5W9",
        "code": "9632", "points": 1,
        "label_ar": "🌈 Tpi.li (+1 نقطة)",          "label_en": "🌈 Tpi.li (+1 Point)"},
    "site_oiiio":      {"url": "https://oii.io/7yIl",
        "code": "4820", "points": 1,
        "label_ar": "💫 Oii.io (+1 نقطة)",          "label_en": "💫 Oii.io (+1 Point)"},
    "site_lnbzla":     {"url": "https://lnbz.la/WIB1cqe",
        "code": "0857", "points": 1,
        "label_ar": "🔗 Lnbz.la (+1 نقطة)",         "label_en": "🔗 Lnbz.la (+1 Point)"},
    "site_linksterr":  {"url": "https://linksterr.com/r/eflthr/",
        "code": "7495", "points": 1,
        "label_ar": "⭐ Linksterr (+1 نقطة)",        "label_en": "⭐ Linksterr (+1 Point)"},
    "site_cpmlink":    {"url": "https://cpmlink.net/v4GoAQ",
        "code": "3652", "points": 1,
        "label_ar": "💰 CPMLink (+1 نقطة)",          "label_en": "💰 CPMLink (+1 Point)"},
    "site_zagl":       {"url": "https://za.gl/XaX1tx",
        "code": "8027", "points": 1,
        "label_ar": "🌍 Za.gl (+1 نقطة)",            "label_en": "🌍 Za.gl (+1 Point)"},
}

DEFAULT_REWARDS = {
    "balance_10": {"points": 80,   "title_ar": "💳 شحن 10 جنيه رصيد",             "title_en": "💳 10 EGP Balance"},
    "balance_20": {"points": 160,  "title_ar": "💳 شحن 20 جنيه رصيد",             "title_en": "💳 20 EGP Balance"},
    "balance_50": {"points": 400,  "title_ar": "💳 شحن 50 جنيه رصيد",             "title_en": "💳 50 EGP Balance"},
    "pubg_60":    {"points": 400,  "title_ar": "🎮 60 شدة ببجي موبايل",            "title_en": "🎮 60 UC PUBG Mobile"},
    "pubg_325":   {"points": 1600, "title_ar": "🎮 325 شدة ببجي موبايل",           "title_en": "🎮 325 UC PUBG Mobile"},
    "pubg_660":   {"points": 3200, "title_ar": "🎮 660 شدة ببجي موبايل",           "title_en": "🎮 660 UC PUBG Mobile"},
    "pubg_1800":  {"points": 8000, "title_ar": "🎮 1800 شدة ببجي موبايل",          "title_en": "🎮 1800 UC PUBG Mobile"},
    "ff_100":     {"points": 400,  "title_ar": "💎 100 جوهرة فري فاير",            "title_en": "💎 100 Diamonds FF"},
    "ff_310":     {"points": 1200, "title_ar": "💎 310 جوهرة فري فاير",            "title_en": "💎 310 Diamonds FF"},
    "ff_520":     {"points": 2000, "title_ar": "💎 520 جوهرة فري فاير",            "title_en": "💎 520 Diamonds FF"},
    "ff_1060":    {"points": 4000, "title_ar": "💎 1060 جوهرة فري فاير",           "title_en": "💎 1060 Diamonds FF"},
}

# ================================================================= #
# 4. TEXTS                                                            #
# ================================================================= #

TEXTS = {
    "ar": {
        "choose_lang": "🌐 اختر لغتك / Choose your language:",
        "welcome":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎮  **بوت الشحن المجاني**  🎮\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👋 أهلاً بك يا **{name}**!\n\n"
            "📌 **كيف يعمل البوت؟**\n"
            "┣ 📋 نفّذ مهمات يومية بسيطة\n"
            "┣ 💎 اجمع نقاط مجاناً\n"
            "┗ 🎁 استبدل النقاط بشحن مجاني\n\n"
            "👇 اختر من القائمة:",
        "sub_required":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ **تنبيه مهم**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "مرحباً **{name}** 👋\n\n"
            "يجب الاشتراك في قناتنا أولاً 🔒\n\n"
            "👇 اشترك ثم اضغط تأكيد:",
        "sub_confirmed": "✅ تم تأكيد اشتراكك بنجاح!",
        "sub_failed":    "❌ لم يتم الاشتراك بعد!",
        "activated":     "🎉 تم تفعيل حسابك!\nاستخدم القائمة أدناه 👇",
        "banned":        "🚫 حسابك موقوف من استخدام البوت.",
        "btn_tasks":     "📋 المهمات",
        "btn_account":   "👤 حسابي",
        "btn_games":     "🎮 شحن ألعاب",
        "btn_balance":   "📱 شحن رصيد",
        "btn_referral":  "👥 دعوة الأصدقاء",
        "btn_tools":     "🛠️ طلب أداة",
        "btn_lang":      "🌐 تغيير اللغة",
        "btn_withdraw":  "💵 سحب دولار",
        "tasks_intro":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 **المهمات اليومية**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📖 **طريقة جمع النقاط:**\n\n"
            "1️⃣ اضغط على الرابط\n"
            "2️⃣ تخطَّ الإعلانات وانتظر العداد\n"
            "3️⃣ انسخ الكود الرباعي\n"
            "4️⃣ أرسله هنا مباشرة ✅\n\n"
            "⏰ كل مهمة مرة كل **24 ساعة**\n"
            "━━━━━━━━━━━━━━━━━━━━━━",
        "task_done":     "✅ **تم!** — {label}",
        "task_wait":
            "⏳ **انتظر قليلاً!**\n\n"
            "🕐 الوقت المتبقي: **{t}**",
        "all_tasks_done":
            "🎊 **أحسنت! أنهيت كل المهمات اليوم!**\n\n"
            "⏰ تفتح مجدداً بعد:\n"
            "**{t}**",
        "account_info":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 **معلومات حسابك**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📝 الاسم: **{name}**\n"
            "🆔 الآيدي: `{user_id}`\n"
            "💎 رصيدك: **{pts}** نقطة\n"
            "👥 دعواتك: **{refs}** شخص\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━",
        "games_title":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎮 **شحن الألعاب**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "اختر الباقة المناسبة 👇",
        "balance_title":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📱 **شحن الرصيد**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "اختر فئة الشحن 👇",
        "code_success":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎉 **أحسنت يا {name}!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ الكود صحيح!\n"
            "💎 تمت إضافة **+{pts}** نقطة\n"
            "📊 رصيدك الآن: **{total}** نقطة",
        "code_wrong":
            "❌ **الكود غير صحيح!**\n\n"
            "تأكد من نسخ الكود الرباعي\n"
            "الظاهر في نهاية الرابط.",
        "not_enough_pts":
            "❌ **نقاطك غير كافية!**\n\n"
            "تحتاج: **{need}** نقطة\n"
            "لديك: **{have}** نقطة",
        "claim_registered": "✅ تم تسجيل طلبك!",
        "claim_ask_data":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 **تأكيد الطلب**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "طلبت: **{title}**\n\n"
            "أرسل في رسالة واحدة:\n"
            "• آيدي اللعبة أو رقم الهاتف\n"
            "• اسمك الكامل\n\n"
            "👇 أرسل البيانات:",
        "claim_sent":
            "✅ **تم إرسال طلبك!**\n\n"
            "سيتم تنفيذه قريباً 🕐",
        "referral_msg":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👥 **نظام الدعوة**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔗 رابط دعوتك:\n`{link}`\n\n"
            "🎁 **{rpts}** نقاط عن كل صديق!\n\n"
            "📊 إحصائياتك:\n"
            "┣ 👥 دعوت: **{count}** شخص\n"
            "┗ 💎 كسبت: **{earned}** نقطة\n"
            "━━━━━━━━━━━━━━━━━━━━━━",
        "referral_bonus":
            "🎉 **مبروك يا {name}!**\n\n"
            "سجلت عبر رابط دعوة 🎊\n"
            "💎 حصلت على **+{pts}** نقاط!\n"
            "📊 رصيدك: **{total}** نقطة",
        "referrer_bonus":
            "🔔 **مبروك!**\n\n"
            "انضم صديق عبر رابطك 🎊\n"
            "💎 **+{pts}** نقطة أضيفت\n"
            "👥 إجمالي دعواتك: **{count}**",
        "referral_need_task":
            "⚠️ **تنبيه**\n\n"
            "الصديق الجديد لازم يكمل\n"
            "مهمة واحدة أولاً عشان\n"
            "تاخد نقاط الدعوة! 💡",
        "referral_max_day":
            "⚠️ وصلت للحد الأقصى للدعوات اليوم!\n"
            "يمكنك دعوة **{max}** أشخاص يومياً فقط.",
        "withdraw_title":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💵 **سحب الدولار**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💱 سعر الدولار: **{rate}** جنيه\n"
            "💸 عمولة الخدمة: **{fee}** جنيه لكل عملية\n\n"
            "📌 اختر الكمية التي تريد سحبها 👇",
        "withdraw_address":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💵 **تفاصيل التحويل**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📦 الطلب: **{amount}$**\n"
            "💰 ستستلم: **{net}** جنيه\n"
            "   ({gross} جنيه - {fee} جنيه عمولة)\n\n"
            "📤 حوّل إلى هذا العنوان:\n"
            "`{address}`\n\n"
            "⚠️ بعد التحويل، أرسل **صورة إثبات السحب** هنا 👇",
        "withdraw_proof_received":
            "✅ **تم استلام إثباتك!**\n\n"
            "سيتم مراجعته وإرسال إثبات الاستلام قريباً 🕐",
        "withdraw_admin_alert":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💵 **طلب سحب دولار جديد!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👤 الاسم: {name}\n"
            "🆔 الآيدي: `{uid}`\n"
            "💵 الكمية: **{amount}$**\n"
            "💰 المبلغ المُحوَّل: **{net}** جنيه\n"
            "━━━━━━━━━━━━━━━━━━━━━━",
    },
    "en": {
        "choose_lang": "🌐 Choose your language / اختر لغتك:",
        "welcome":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎮  **Free Top-Up Bot**  🎮\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👋 Welcome **{name}**!\n\n"
            "📌 **How it works:**\n"
            "┣ 📋 Complete daily tasks\n"
            "┣ 💎 Earn free points\n"
            "┗ 🎁 Redeem for free top-ups\n\n"
            "👇 Choose from the menu:",
        "sub_required":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ **Important Notice**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Hello **{name}** 👋\n\n"
            "Join our channel first 🔒\n\n"
            "👇 Join then confirm:",
        "sub_confirmed": "✅ Subscription confirmed!",
        "sub_failed":    "❌ Not subscribed yet!",
        "activated":     "🎉 Account activated!\nUse the menu below 👇",
        "banned":        "🚫 Your account has been suspended.",
        "btn_tasks":     "📋 Tasks",
        "btn_account":   "👤 My Account",
        "btn_games":     "🎮 Game Top-Up",
        "btn_balance":   "📱 Balance Top-Up",
        "btn_referral":  "👥 Invite Friends",
        "btn_tools":     "🛠️ Request Tool",
        "btn_lang":      "🌐 Change Language",
        "btn_withdraw":  "💵 Dollar Withdrawal",
        "tasks_intro":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📋 **Daily Tasks**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📖 **How to earn:**\n\n"
            "1️⃣ Tap a link\n"
            "2️⃣ Skip ads, wait for timer\n"
            "3️⃣ Copy the 4-digit code\n"
            "4️⃣ Send it here ✅\n\n"
            "⏰ Each task once every **24h**\n"
            "━━━━━━━━━━━━━━━━━━━━━━",
        "task_done":     "✅ **Done!** — {label}",
        "task_wait":
            "⏳ **Wait!**\n\n"
            "🕐 Time left: **{t}**",
        "all_tasks_done":
            "🎊 **Great! All tasks done today!**\n\n"
            "⏰ Opens again in:\n"
            "**{t}**",
        "account_info":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 **Your Account**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📝 Name: **{name}**\n"
            "🆔 ID: `{user_id}`\n"
            "💎 Points: **{pts}**\n"
            "👥 Referrals: **{refs}**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━",
        "games_title":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎮 **Game Top-Up**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Choose your package 👇",
        "balance_title":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📱 **Balance Top-Up**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Choose amount 👇",
        "code_success":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎉 **Great job {name}!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ Correct code!\n"
            "💎 **+{pts}** point(s) added\n"
            "📊 Balance: **{total}** points",
        "code_wrong":
            "❌ **Wrong code!**\n\n"
            "Copy the 4-digit code\n"
            "from the end of the link.",
        "not_enough_pts":
            "❌ **Not enough points!**\n\n"
            "Need: **{need}**\n"
            "Have: **{have}**",
        "claim_registered": "✅ Request registered!",
        "claim_ask_data":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📝 **Confirm Request**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Requested: **{title}**\n\n"
            "Send in one message:\n"
            "• Game ID or phone number\n"
            "• Your full name\n\n"
            "👇 Send details:",
        "claim_sent":
            "✅ **Request sent!**\n\n"
            "Will be fulfilled soon 🕐",
        "referral_msg":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "👥 **Referral System**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔗 Your link:\n`{link}`\n\n"
            "🎁 **{rpts}** points per friend!\n\n"
            "📊 Stats:\n"
            "┣ 👥 Invited: **{count}**\n"
            "┗ 💎 Earned: **{earned}** pts\n"
            "━━━━━━━━━━━━━━━━━━━━━━",
        "referral_bonus":
            "🎉 **Congrats {name}!**\n\n"
            "Joined via referral 🎊\n"
            "💎 Got **+{pts}** bonus points!\n"
            "📊 Balance: **{total}**",
        "referrer_bonus":
            "🔔 **Great!**\n\n"
            "New friend joined via your link 🎊\n"
            "💎 **+{pts}** points added\n"
            "👥 Total: **{count}**",
        "referral_need_task":
            "⚠️ **Notice**\n\n"
            "Your friend must complete\n"
            "one task first to unlock\n"
            "your referral points! 💡",
        "referral_max_day":
            "⚠️ Daily referral limit reached!\n"
            "Max **{max}** referrals per day.",
        "withdraw_title":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💵 **Dollar Withdrawal**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💱 Dollar rate: **{rate}** EGP\n"
            "💸 Service fee: **{fee}** EGP per transaction\n\n"
            "📌 Choose amount to withdraw 👇",
        "withdraw_address":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💵 **Transfer Details**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📦 Amount: **{amount}$**\n"
            "💰 You receive: **{net}** EGP\n"
            "   ({gross} EGP - {fee} EGP fee)\n\n"
            "📤 Transfer to this address:\n"
            "`{address}`\n\n"
            "⚠️ After transferring, send a **withdrawal proof screenshot** here 👇",
        "withdraw_proof_received":
            "✅ **Proof received!**\n\n"
            "Will be reviewed and confirmed soon 🕐",
        "withdraw_admin_alert":
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "💵 **New Dollar Withdrawal!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👤 Name: {name}\n"
            "🆔 ID: `{uid}`\n"
            "💵 Amount: **{amount}$**\n"
            "💰 Transferred: **{net}** EGP\n"
            "━━━━━━━━━━━━━━━━━━━━━━",
    }
}

def t(uid, key, **kwargs):
    lang = get_user_lang(uid)
    text = TEXTS.get(lang, TEXTS["ar"]).get(key, key)
    return text.format(**kwargs) if kwargs else text

# ================================================================= #
# 5. DATABASE                                                         #
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
            user_id           INTEGER PRIMARY KEY,
            username          TEXT,
            first_name        TEXT,
            points            INTEGER DEFAULT 0,
            is_banned         INTEGER DEFAULT 0,
            lang              TEXT DEFAULT 'ar',
            referred_by       INTEGER DEFAULT NULL,
            referral_count    INTEGER DEFAULT 0,
            referral_pts      INTEGER DEFAULT 0,
            referral_day      TEXT DEFAULT NULL,
            referral_day_count INTEGER DEFAULT 0,
            first_task_done   INTEGER DEFAULT 0,
            joined_at         TEXT DEFAULT (datetime('now'))
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

        c.execute('''CREATE TABLE IF NOT EXISTS links (
            link_key  TEXT PRIMARY KEY,
            url       TEXT,
            code      TEXT,
            points    INTEGER DEFAULT 1,
            label_ar  TEXT,
            label_en  TEXT,
            is_active INTEGER DEFAULT 1
        )''')

        # هجرة تلقائية للأعمدة الجديدة
        migrations = [
            ("lang",               "TEXT DEFAULT 'ar'"),
            ("referred_by",        "INTEGER DEFAULT NULL"),
            ("referral_count",     "INTEGER DEFAULT 0"),
            ("referral_pts",       "INTEGER DEFAULT 0"),
            ("referral_day",       "TEXT DEFAULT NULL"),
            ("referral_day_count", "INTEGER DEFAULT 0"),
            ("first_task_done",    "INTEGER DEFAULT 0"),
            ("joined_at",          "TEXT DEFAULT (datetime('now'))"),
        ]
        for col, definition in migrations:
            try:
                c.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
            except sqlite3.OperationalError:
                pass

        # ملء الروابط
        c.execute('SELECT COUNT(*) FROM links')
        if c.fetchone()[0] == 0:
            for key, info in DEFAULT_LINKS.items():
                c.execute('INSERT INTO links VALUES (?,?,?,?,?,?,1)',
                    (key, info["url"], info["code"], info["points"],
                     info["label_ar"], info["label_en"]))

        # ملء المكافآت
        c.execute('SELECT COUNT(*) FROM rewards')
        if c.fetchone()[0] == 0:
            for key, info in DEFAULT_REWARDS.items():
                c.execute('INSERT INTO rewards VALUES (?,?,?,?)',
                    (key, info["points"], info["title_ar"], info["title_en"]))

        c.execute('INSERT OR IGNORE INTO settings VALUES (?,?)', ('channel_id',   str(DEFAULT_CHANNEL_ID)))
        c.execute('INSERT OR IGNORE INTO settings VALUES (?,?)', ('channel_link', DEFAULT_CHANNEL_LINK))

        conn.commit()
        conn.close()

# ── DB Helpers ───────────────────────────────────────────────────── #

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

# ================================================================= #
# STICKERS — بعد get_setting عشان تشتغل صح                          #
# ================================================================= #

def send_sticker(chat_id, sticker_key):
    """يبعت ستيكر لو موجود في الإعدادات"""
    file_id = get_setting(f"sticker_{sticker_key}")
    if file_id and file_id.strip():
        try:
            bot.send_sticker(chat_id, file_id)
            return True
        except Exception:
            pass
    return False

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
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT 1 FROM users WHERE user_id=?', (user_id,))
        if c.fetchone():
            conn.close()
            return False
        c.execute(
            'INSERT INTO users (user_id,username,first_name,points,referred_by) VALUES (?,?,?,0,?)',
            (user_id, username or "None", first_name or "User", referred_by))
        conn.commit()
        conn.close()
    return True

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
            c.execute('UPDATE users SET points=MAX(0,points+?) WHERE user_id=?', (delta, user_id))
        else:
            c.execute('UPDATE users SET points=points+? WHERE user_id=?', (delta, user_id))
        conn.commit()
        conn.close()

def get_user_info(user_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id,username,first_name,points,is_banned,lang,referred_by,referral_count,referral_pts,joined_at,first_task_done FROM users WHERE user_id=?', (user_id,))
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

def get_top_users(limit=10):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT user_id,first_name,points FROM users WHERE is_banned=0 ORDER BY points DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        conn.close()
    return rows

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

def mark_first_task_done(user_id):
    with db_lock:
        conn = get_connection()
        conn.execute('UPDATE users SET first_task_done=1 WHERE user_id=?', (user_id,))
        conn.commit()
        conn.close()

def get_first_task_done(user_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT first_task_done FROM users WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
    return bool(row and row[0])

def get_referred_by(user_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT referred_by FROM users WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
    return row[0] if row else None

def check_referral_day_limit(referrer_id):
    """فحص إذا وصل المستخدم للحد اليومي للدعوات"""
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT referral_day, referral_day_count FROM users WHERE user_id=?', (referrer_id,))
        row = c.fetchone()
        conn.close()
    if not row:
        return True
    today = datetime.now().strftime("%Y-%m-%d")
    ref_day, ref_count = row
    if ref_day != today:
        return True  # يوم جديد
    return ref_count < MAX_REFERRALS_DAY

def add_referral_to_referrer(referrer_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        c.execute('SELECT referral_day, referral_day_count FROM users WHERE user_id=?', (referrer_id,))
        row = c.fetchone()
        if row:
            ref_day, ref_count = row
            new_count = 1 if ref_day != today else ref_count + 1
            conn.execute(
                'UPDATE users SET referral_count=referral_count+1, referral_pts=referral_pts+?, '
                'points=points+?, referral_day=?, referral_day_count=? WHERE user_id=?',
                (REFERRAL_POINTS, REFERRAL_POINTS, today, new_count, referrer_id))
        conn.commit()
        conn.close()

def get_referral_info(user_id):
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT referral_count,referral_pts FROM users WHERE user_id=?', (user_id,))
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
            'INSERT OR REPLACE INTO task_logs (user_id,task_key,completion_time) VALUES (?,?,?)',
            (user_id, task_key, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()

def get_next_task_open_time(user_id):
    """أقرب وقت تُفتح فيه مهمة جديدة"""
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT MIN(completion_time) FROM task_logs WHERE user_id=?', (user_id,))
        row = c.fetchone()
        conn.close()
    if row and row[0]:
        earliest = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        opens_at = earliest + timedelta(hours=24)
        if opens_at > datetime.now():
            remaining = opens_at - datetime.now()
            h, rem = divmod(int(remaining.total_seconds()), 3600)
            m = rem // 60
            return f"{h} ساعة و {m} دقيقة"
    return None

# ── Links DB ─────────────────────────────────────────────────────── #

def load_links_from_db():
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT link_key,url,code,points,label_ar,label_en,is_active FROM links ORDER BY rowid')
        rows = c.fetchall()
        conn.close()
    return {r[0]:{"url":r[1],"code":r[2],"points":r[3],"label_ar":r[4],"label_en":r[5],"is_active":r[6]} for r in rows}

def add_link_to_db(key, url, code, points, label_ar, label_en):
    with db_lock:
        conn = get_connection()
        conn.execute('INSERT OR REPLACE INTO links VALUES (?,?,?,?,?,?,1)',
                     (key, url, code, points, label_ar, label_en))
        conn.commit()
        conn.close()

def update_link_in_db(key, field, value):
    with db_lock:
        conn = get_connection()
        conn.execute(f'UPDATE links SET {field}=? WHERE link_key=?', (value, key))
        conn.commit()
        conn.close()

def delete_link_from_db(key):
    with db_lock:
        conn = get_connection()
        conn.execute('DELETE FROM links WHERE link_key=?', (key,))
        conn.commit()
        conn.close()

# ── Rewards DB ───────────────────────────────────────────────────── #

def load_rewards_from_db():
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT reward_key,points,title_ar,title_en FROM rewards')
        rows = c.fetchall()
        conn.close()
    return {r[0]:{"points":r[1],"title_ar":r[2],"title_en":r[3]} for r in rows}

def update_reward_price_in_db(reward_key, new_points):
    with db_lock:
        conn = get_connection()
        conn.execute('UPDATE rewards SET points=? WHERE reward_key=?', (new_points, reward_key))
        conn.commit()
        conn.close()

def add_reward_to_db(key, points, title_ar, title_en):
    with db_lock:
        conn = get_connection()
        conn.execute('INSERT OR REPLACE INTO rewards VALUES (?,?,?,?)', (key, points, title_ar, title_en))
        conn.commit()
        conn.close()

def delete_reward_from_db(key):
    with db_lock:
        conn = get_connection()
        conn.execute('DELETE FROM rewards WHERE reward_key=?', (key,))
        conn.commit()
        conn.close()

# ── Charge Requests ──────────────────────────────────────────────── #

def save_charge_request(user_id, reward_key, user_data):
    with db_lock:
        conn = get_connection()
        conn.execute('INSERT INTO charge_requests (user_id,reward_key,user_data) VALUES (?,?,?)',
                     (user_id, reward_key, user_data))
        conn.commit()
        conn.close()

def get_pending_requests():
    with db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('SELECT id,user_id,reward_key,user_data,created_at FROM charge_requests WHERE status="pending" ORDER BY id DESC LIMIT 20')
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
# 6. SUBSCRIPTION CHECK                                               #
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
# 7. KEYBOARDS                                                        #
# ================================================================= #

def get_lang_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇸🇦 العربية", callback_data="setlang_ar"),
        types.InlineKeyboardButton("🇬🇧 English",  callback_data="setlang_en")
    )
    return markup

def get_main_keyboard(uid):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton(t(uid, "btn_tasks")),
        types.KeyboardButton(t(uid, "btn_account")),
        types.KeyboardButton(t(uid, "btn_games")),
        types.KeyboardButton(t(uid, "btn_balance")),
        types.KeyboardButton(t(uid, "btn_withdraw")),
        types.KeyboardButton(t(uid, "btn_tools")),
        types.KeyboardButton(t(uid, "btn_lang"))
    )
    return markup

def get_subscription_keyboard(uid):
    lang = get_user_lang(uid)
    join_text    = "📢 اشترك في القناة" if lang == "ar" else "📢 Join Channel"
    confirm_text = "✅ تأكيد الاشتراك"   if lang == "ar" else "✅ Confirm"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(join_text,    url=get_channel_link()),
        types.InlineKeyboardButton(confirm_text, callback_data="check_sub")
    )
    return markup

def get_tasks_keyboard(uid):
    """كل مهمة رسالة منفردة مع حالتها"""
    lang  = get_user_lang(uid)
    links = load_links_from_db()
    markup = types.InlineKeyboardMarkup(row_width=1)
    all_done = True
    for key, info in links.items():
        if not info["is_active"]:
            continue
        allowed, wait_time = check_task_cooldown(uid, key)
        if allowed:
            all_done = False
            label = info["label_ar"] if lang == "ar" else info["label_en"]
            markup.add(types.InlineKeyboardButton(
                f"🔗 {label}", url=info["url"]))
        # لو خلص المهمة مش بنضيفها للأزرار — تختفي تلقائي
    return markup, all_done

def get_rewards_keyboard(uid, reward_type):
    lang    = get_user_lang(uid)
    markup  = types.InlineKeyboardMarkup(row_width=1)
    rewards = load_rewards_from_db()
    for key, info in rewards.items():
        show = (reward_type == "games"   and ("pubg" in key or "ff" in key)) or \
               (reward_type == "balance" and "balance" in key) or \
               (reward_type == "tools"   and "tool" in key)
        if show:
            title = info["title_ar"] if lang == "ar" else info["title_en"]
            markup.add(types.InlineKeyboardButton(
                f"🎁 {title}  ┃  {info['points']} نقطة",
                callback_data=f"claim_{key}"))
    return markup

# ================================================================= #
# 8. GUARD                                                            #
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
# 9. /start                                                           #
# ================================================================= #

@bot.message_handler(commands=['start'])
def handle_start(message):
    uid   = message.from_user.id
    uname = message.from_user.username or "None"
    fname = message.from_user.first_name or "User"

    args        = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
            if referrer_id == uid:
                referrer_id = None
        except ValueError:
            referrer_id = None

    is_new = add_user_if_not_exists(uid, uname, fname, referred_by=referrer_id)

    if is_user_banned(uid):
        bot.send_message(message.chat.id, t(uid, "banned"))
        return

    if is_new:
        bot.send_message(message.chat.id,
            TEXTS["ar"]["choose_lang"] + "\n" + TEXTS["en"]["choose_lang"],
            reply_markup=get_lang_keyboard())
        return

    if not check_forced_subscription(uid):
        bot.send_message(message.chat.id,
            t(uid, "sub_required", name=fname),
            reply_markup=get_subscription_keyboard(uid), parse_mode="Markdown")
        return

    send_sticker(message.chat.id, "welcome")
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
# 10. MAIN USER HANDLER                                               #
# ================================================================= #

@bot.message_handler(func=lambda m: True)
def handle_user_actions(message):
    uid   = message.from_user.id
    fname = message.from_user.first_name or "User"
    uname = message.from_user.username  or "None"
    add_user_if_not_exists(uid, uname, fname)

    if message.text == "/admin" and uid == DEVELOPER_ID:
        show_admin_panel(message.chat.id)
        return

    if not guard(message):
        return

    text = message.text

    if text in (TEXTS["ar"]["btn_lang"], TEXTS["en"]["btn_lang"]):
        bot.send_message(message.chat.id,
            TEXTS["ar"]["choose_lang"] + "\n" + TEXTS["en"]["choose_lang"],
            reply_markup=get_lang_keyboard())

    elif text in (TEXTS["ar"]["btn_tasks"], TEXTS["en"]["btn_tasks"]):
        send_tasks_message(message.chat.id, uid, fname)

    elif text in (TEXTS["ar"]["btn_account"], TEXTS["en"]["btn_account"]):
        pts     = get_user_points(uid)
        refs, _ = get_referral_info(uid)
        bot.send_message(message.chat.id,
            t(uid, "account_info", name=fname, user_id=uid, pts=pts, refs=refs),
            parse_mode="Markdown")

    elif text in (TEXTS["ar"]["btn_games"], TEXTS["en"]["btn_games"]):
        bot.send_message(message.chat.id,
            t(uid, "games_title"),
            reply_markup=get_rewards_keyboard(uid, "games"),
            parse_mode="Markdown")

    elif text in (TEXTS["ar"]["btn_balance"], TEXTS["en"]["btn_balance"]):
        bot.send_message(message.chat.id,
            t(uid, "balance_title"),
            reply_markup=get_rewards_keyboard(uid, "balance"),
            parse_mode="Markdown")

    elif text in (TEXTS["ar"]["btn_referral"], TEXTS["en"]["btn_referral"]):
        ref_link = f"https://t.me/{bot.get_me().username}?start=ref_{uid}"
        count, earned = get_referral_info(uid)
        bot.send_message(message.chat.id,
            t(uid, "referral_msg", link=ref_link, rpts=REFERRAL_POINTS,
              count=count, earned=earned),
            parse_mode="Markdown")

    elif text in (TEXTS["ar"]["btn_withdraw"], TEXTS["en"]["btn_withdraw"]):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for amount in [1, 2, 5, 10]:
            gross = amount * DOLLAR_RATE
            net   = gross - (DOLLAR_FEE * amount)  # 10 جنيه على كل دولار
            markup.add(types.InlineKeyboardButton(
                f"💵 {amount}$ ← تستلم {net} جنيه",
                callback_data=f"withdraw_{amount}"))
        bot.send_message(message.chat.id,
            t(uid, "withdraw_title", rate=DOLLAR_RATE, fee=DOLLAR_FEE),
            reply_markup=markup, parse_mode="Markdown")

    elif text in (TEXTS["ar"]["btn_tools"], TEXTS["en"]["btn_tools"]):
        cur_pts = get_user_points(uid)
        markup  = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(
            "🛠️ طلب أداة / كود  ┃  60 نقطة",
            callback_data="claim_tool_req"))
        tool_msg = (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🛠️ **طلب أداة / كود**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 **كيف يعمل؟**\n"
            "┣ تضغط على الزر أدناه\n"
            "┣ يتم خصم 60 نقطة\n"
            "┣ يوصلك رسالة من الأدمن على الخاص\n"
            "┗ تقوله اللي انت عايزه\n\n"
            f"💎 رصيدك الحالي: **{cur_pts}** نقطة"
        )
        bot.send_message(message.chat.id,
            tool_msg, reply_markup=markup, parse_mode="Markdown")

    else:
        handle_code_input(message, uid, fname)

# ── إرسال رسالة المهمات ───────────────────────────────────────────── #

def send_tasks_message(chat_id, uid, fname):
    markup, all_done = get_tasks_keyboard(uid)

    if all_done:
        wait_time = get_next_task_open_time(uid)
        wait_str  = wait_time or "قريباً"
        send_sticker(chat_id, "wait")
        bot.send_message(chat_id,
            t(uid, "all_tasks_done", t=wait_str),
            parse_mode="Markdown")
        return

    send_sticker(chat_id, "tasks")
    bot.send_message(chat_id,
        t(uid, "tasks_intro"),
        reply_markup=markup,
        parse_mode="Markdown")

# ── معالجة الأكواد ────────────────────────────────────────────────── #

def handle_code_input(message, uid, fname):
    text  = message.text
    links = load_links_from_db()

    for task_key, info in links.items():
        if not info["is_active"]:
            continue
        if info["code"] in ("", "channel_redirect"):
            continue
        if text == info["code"]:
            allowed, wait_time = check_task_cooldown(uid, task_key)
            if not allowed:
                bot.send_message(message.chat.id,
                    t(uid, "task_wait", t=wait_time), parse_mode="Markdown")
            else:
                update_user_points(uid, info["points"])
                save_task_completion(uid, task_key)
                total = get_user_points(uid)

                # أول مهمة يكملها — فعّل نقاط الدعوة للمن دعاه
                if not get_first_task_done(uid):
                    mark_first_task_done(uid)
                    referrer_id = get_referred_by(uid)
                    if referrer_id and user_exists(referrer_id):
                        if check_referral_day_limit(referrer_id):
                            add_referral_to_referrer(referrer_id)
                            ref_count, _ = get_referral_info(referrer_id)
                            try:
                                bot.send_message(referrer_id,
                                    t(referrer_id, "referrer_bonus",
                                      pts=REFERRAL_POINTS, count=ref_count),
                                    parse_mode="Markdown")
                            except Exception:
                                pass
                        else:
                            try:
                                bot.send_message(referrer_id,
                                    t(referrer_id, "referral_max_day",
                                      max=MAX_REFERRALS_DAY),
                                    parse_mode="Markdown")
                            except Exception:
                                pass

                send_sticker(message.chat.id, "success")
                bot.send_message(message.chat.id,
                    t(uid, "code_success", name=fname, pts=info["points"], total=total),
                    parse_mode="Markdown")

                # تحديث رسالة المهمات — أرسل الجديدة بدون المهمة المنجزة
                new_markup, new_all_done = get_tasks_keyboard(uid)
                if new_all_done:
                    wait_time = get_next_task_open_time(uid)
                    bot.send_message(message.chat.id,
                        t(uid, "all_tasks_done", t=wait_time or "قريباً"),
                        parse_mode="Markdown")
                else:
                    lang = get_user_lang(uid)
                    remaining = sum(1 for k, v in load_links_from_db().items()
                                   if v["is_active"] and check_task_cooldown(uid, k)[0]
                                   and v["code"] not in ("", "channel_redirect"))
                    bot.send_message(message.chat.id,
                        f"📋 **المهمات المتبقية: {remaining}**\n👇",
                        reply_markup=new_markup, parse_mode="Markdown")
            return

    bot.send_message(message.chat.id, t(uid, "code_wrong"))

# ================================================================= #
# 11. REWARDS CLAIM                                                   #
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
            t(uid, "not_enough_pts", need=info["points"], have=user_pts),
            show_alert=True)
        return
    update_user_points(uid, -info["points"])
    bot.answer_callback_query(call.id, t(uid, "claim_registered"), show_alert=True)
    title = info["title_ar"] if lang == "ar" else info["title_en"]
    msg = bot.send_message(call.message.chat.id,
        t(uid, "claim_ask_data", title=title), parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_user_delivery_data, reward_key, info["points"])

def process_user_delivery_data(message, reward_key, points_cost):
    uid         = message.from_user.id
    user_input  = message.text or "(لا يوجد نص)"
    rewards     = load_rewards_from_db()
    reward_info = rewards.get(reward_key, {})
    save_charge_request(uid, reward_key, user_input)
    admin_alert = (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🚨 **طلب شحن جديد!**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 الاسم: {message.from_user.first_name}\n"
        f"🆔 الآيدي: `{uid}`\n"
        f"📦 الطلب: **{reward_info.get('title_ar','؟')}**\n"
        f"💎 النقاط: {points_cost}\n"
        f"📌 البيانات: `{user_input}`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
    )
    try:
        bot.send_message(DEVELOPER_ID, admin_alert, parse_mode="Markdown")
    except Exception as e:
        print(f"[ERROR] {e}")
    send_sticker(message.chat.id, "reward")
    bot.send_message(message.chat.id,
        t(uid, "claim_sent"), reply_markup=get_main_keyboard(uid))

# ================================================================= #
# 11b. DOLLAR WITHDRAWAL FLOW                                         #
# ================================================================= #

@bot.callback_query_handler(func=lambda c: c.data.startswith("withdraw_"))
def handle_withdraw_amount(call):
    uid   = call.from_user.id
    fname = call.from_user.first_name or "User"
    try:
        amount = int(call.data.replace("withdraw_", ""))
    except ValueError:
        return
    gross = amount * DOLLAR_RATE
    net   = gross - (DOLLAR_FEE * amount)
    bot.answer_callback_query(call.id)
    wallet = get_setting('wallet_address') or WALLET_ADDRESS
    # الخطوة 1: أرسلله عنوان محفظتك عشان يبعتلك
    msg = bot.send_message(call.message.chat.id,
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💵 **تفاصيل طلب السحب**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 المبلغ: **{amount}$**\n"
        f"💸 بعد العمولة: **{net} جنيه**\n\n"
        f"📌 **خطوات السحب:**\n"
        f"1️⃣ حول **{amount}$** على هذا العنوان:\n"
        f"`{wallet}`\n\n"
        f"2️⃣ اكتب **نوع الشبكة** اللي بعت عليها\n"
        f"(TRC20 / BEP20 / ERC20)\n\n"
        f"👇 اكتب نوع الشبكة الآن:",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_withdraw_network, amount, net, fname)

def process_withdraw_network(message, amount, net, fname):
    """الخطوة 2: يكتب نوع الشبكة"""
    uid     = message.from_user.id
    network = message.text.strip().upper()
    valid   = ["TRC20", "BEP20", "ERC20", "TRC-20", "BEP-20", "ERC-20"]
    if network not in valid:
        msg = bot.send_message(message.chat.id,
            "❌ نوع الشبكة غير صحيح!\n\n"
            "اكتب واحدة من:\n"
            "• TRC20\n• BEP20\n• ERC20",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_withdraw_network, amount, net, fname)
        return
    msg = bot.send_message(message.chat.id,
        f"✅ الشبكة: **{network}**\n\n"
        f"📸 **الآن ابعت صورة إثبات** إنك حولت الـ {amount}$ 👇",
        parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_withdraw_proof, amount, net, network, fname)

def process_withdraw_proof(message, amount, net, network, fname):
    """الخطوة 3: يبعت إثبات التحويل"""
    uid = message.from_user.id
    uname = message.from_user.username or "بدون يوزر"
    if message.content_type != 'photo':
        msg = bot.send_message(message.chat.id,
            "❌ يرجى إرسال **صورة** إثبات التحويل فقط.",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_withdraw_proof, amount, net, network, fname)
        return
    file_id = message.photo[-1].file_id
    # أبلّغ المستخدم
    bot.send_message(message.chat.id,
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ **تم استلام إثبات التحويل!**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⏳ جاري المراجعة والتحويل...\n"
        "ستصلك رسالة عند اكتمال العملية 🕐",
        reply_markup=get_main_keyboard(uid), parse_mode="Markdown")
    # أبعت للأدمن
    try:
        bot.send_message(DEVELOPER_ID,
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 **طلب سحب دولار جديد!**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 الاسم: **{fname}**\n"
            f"🆔 الآيدي: `{uid}`\n"
            f"📱 اليوزر: @{uname}\n"
            f"💰 المبلغ: **{amount}$**\n"
            f"🌐 الشبكة: **{network}**\n"
            f"💸 بعد العمولة: **{net} جنيه**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📸 إثبات التحويل أدناه 👇",
            parse_mode="Markdown")
        bot.send_photo(DEVELOPER_ID, file_id,
            caption=f"✅ بعد المراجعة ابعت له إثبات التحويل على الخاص @{uname}",
            parse_mode="Markdown")
    except Exception as e:
        print(f"[WITHDRAW ERROR] {e}")



def show_admin_panel(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📊  إحصائيات البوت",              callback_data="adm_stats"),
        types.InlineKeyboardButton("🏆  Top 10 مستخدمين",             callback_data="adm_top10"),
        types.InlineKeyboardButton("📋  الطلبات المعلقة",              callback_data="adm_pending"),
        types.InlineKeyboardButton("🔗  إدارة الروابط والأكواد",       callback_data="adm_links"),
        types.InlineKeyboardButton("🎁  إدارة المكافآت والأسعار",      callback_data="adm_rewards"),
        types.InlineKeyboardButton("📺  تعديل بيانات القناة",          callback_data="adm_change_channel"),
        types.InlineKeyboardButton("🔍  البحث عن مستخدم",              callback_data="adm_search_user"),
        types.InlineKeyboardButton("➕  إضافة نقاط لمستخدم",           callback_data="adm_add_points"),
        types.InlineKeyboardButton("➖  خصم نقاط من مستخدم",           callback_data="adm_remove_points"),
        types.InlineKeyboardButton("🚫  حظر مستخدم",                   callback_data="adm_ban_user"),
        types.InlineKeyboardButton("✅  رفع حظر مستخدم",                callback_data="adm_unban_user"),
        types.InlineKeyboardButton("📤  إرسال إثبات شحن لعميل",        callback_data="adm_send_proof"),
        types.InlineKeyboardButton("📢  إذاعة جماعية",                 callback_data="adm_broadcast"),
        types.InlineKeyboardButton("🎭  إدارة الستيكرات",                callback_data="adm_stickers"),
        types.InlineKeyboardButton("💵  تعديل عنوان المحفظة",            callback_data="adm_wallet"),
    )
    bot.send_message(chat_id,
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑  **لوحة تحكم الإدارة**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "اختر العملية المطلوبة 👇",
        reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c:
    c.data.startswith("adm_") or c.data.startswith("req-") or
    c.data.startswith("editprice_") or c.data.startswith("lnk_") or
    c.data.startswith("rwd_") or c.data.startswith("stk_")
)
def handle_admin_callbacks(call):
    if call.from_user.id != DEVELOPER_ID:
        bot.answer_callback_query(call.id, "🚫 ليس لديك صلاحية!", show_alert=True)
        return
    action = call.data
    bot.answer_callback_query(call.id)

    if action == "adm_stats":
        total = get_total_users_count()
        with db_lock:
            conn = get_connection()
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM users WHERE is_banned=1')
            banned = c.fetchone()[0]
            c.execute('SELECT COUNT(*) FROM charge_requests WHERE status="pending"')
            pending = c.fetchone()[0]
            c.execute('SELECT COUNT(*) FROM charge_requests WHERE status="done"')
            done = c.fetchone()[0]
            c.execute('SELECT SUM(points) FROM users')
            total_pts = c.fetchone()[0] or 0
            conn.close()
        bot.send_message(call.message.chat.id,
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 **إحصائيات البوت**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👥 المستخدمون: **{total}**\n"
            f"🚫 محظورون: **{banned}**\n"
            f"💎 إجمالي النقاط: **{total_pts}**\n"
            f"📋 طلبات معلقة: **{pending}**\n"
            f"✅ طلبات منجزة: **{done}**\n"
            "━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown")

    elif action == "adm_top10":
        top    = get_top_users(10)
        medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        text   = "━━━━━━━━━━━━━━━━━━━━━━\n🏆 **Top 10**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, (uid, fname, pts) in enumerate(top):
            text += f"{medals[i]} **{fname}** — `{uid}`\n    💎 {pts} نقطة\n\n"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

    elif action == "adm_pending":
        requests = get_pending_requests()
        if not requests:
            bot.send_message(call.message.chat.id, "✅ لا توجد طلبات معلقة.")
            return
        rewards = load_rewards_from_db()
        for req in requests:
            req_id, user_id, reward_key, user_data, created_at = req
            title = rewards.get(reward_key, {}).get('title_ar', reward_key)
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("✅ تم",  callback_data=f"req-done-{req_id}-{user_id}"),
                types.InlineKeyboardButton("❌ رفض", callback_data=f"req-reject-{req_id}-{user_id}")
            )
            bot.send_message(call.message.chat.id,
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔔 **طلب #{req_id}**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 آيدي: `{user_id}`\n"
                f"📦 الطلب: **{title}**\n"
                f"📌 البيانات: `{user_data}`\n"
                f"🕐 التاريخ: {created_at}",
                reply_markup=markup, parse_mode="Markdown")

    elif action == "adm_links":
        links  = load_links_from_db()
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, info in links.items():
            status = "✅" if info["is_active"] else "🔴"
            markup.add(types.InlineKeyboardButton(
                f"{status} {info['label_ar']}", callback_data=f"lnk_edit_{key}"))
        markup.add(types.InlineKeyboardButton("➕ إضافة رابط جديد", callback_data="lnk_add"))
        bot.send_message(call.message.chat.id,
            "━━━━━━━━━━━━━━━━━━━━━━\n🔗 **إدارة الروابط**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ مفعل  |  🔴 معطل\n\nاضغط للتعديل 👇",
            reply_markup=markup, parse_mode="Markdown")

    elif action == "lnk_add":
        msg = bot.send_message(call.message.chat.id,
            "➕ **إضافة رابط جديد**\n\n"
            "أرسل 6 أسطر بالترتيب:\n"
            "1. مفتاح (مثال: site_new)\n"
            "2. الرابط\n3. الكود (أو NONE)\n"
            "4. النقاط\n5. الاسم عربي\n6. الاسم إنجليزي",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, admin_add_link_handler)

    elif action.startswith("lnk_edit_"):
        key   = action.replace("lnk_edit_", "")
        links = load_links_from_db()
        info  = links.get(key, {})
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("✏️ تعديل URL",         callback_data=f"lnk_url_{key}"),
            types.InlineKeyboardButton("🔢 تعديل الكود",        callback_data=f"lnk_code_{key}"),
            types.InlineKeyboardButton("💎 تعديل النقاط",       callback_data=f"lnk_pts_{key}"),
            types.InlineKeyboardButton("🏷️ اسم عربي",         callback_data=f"lnk_lar_{key}"),
            types.InlineKeyboardButton("🏷️ اسم إنجليزي",     callback_data=f"lnk_len_{key}"),
            types.InlineKeyboardButton(
                "🔴 تعطيل" if info.get("is_active") else "✅ تفعيل",
                callback_data=f"lnk_toggle_{key}"),
            types.InlineKeyboardButton("🗑️ حذف",              callback_data=f"lnk_del_{key}"),
            types.InlineKeyboardButton("🔙 رجوع",               callback_data="adm_links"),
        )
        bot.send_message(call.message.chat.id,
            f"🔗 **{info.get('label_ar','؟')}**\n"
            f"🌐 {info.get('url','؟')}\n"
            f"🔢 الكود: `{info.get('code','؟')}`\n"
            f"💎 النقاط: {info.get('points','؟')}\n"
            f"الحالة: {'✅' if info.get('is_active') else '🔴'}",
            reply_markup=markup, parse_mode="Markdown")

    elif action.startswith("lnk_toggle_"):
        key     = action.replace("lnk_toggle_", "")
        links   = load_links_from_db()
        info    = links.get(key, {})
        new_val = 0 if info.get("is_active") else 1
        update_link_in_db(key, "is_active", new_val)
        bot.send_message(call.message.chat.id,
            f"{'✅ تفعيل' if new_val else '🔴 تعطيل'}: **{info.get('label_ar','؟')}**",
            parse_mode="Markdown")

    elif action.startswith("lnk_del_"):
        key = action.replace("lnk_del_", "")
        links = load_links_from_db()
        info  = links.get(key, {})
        delete_link_from_db(key)
        bot.send_message(call.message.chat.id,
            f"🗑️ تم حذف: **{info.get('label_ar','؟')}**", parse_mode="Markdown")

    elif action.startswith("lnk_url_"):
        key = action.replace("lnk_url_", "")
        msg = bot.send_message(call.message.chat.id, f"🌐 أرسل الرابط الجديد:")
        bot.register_next_step_handler(msg, partial(admin_update_link_field, link_key=key, field="url"))

    elif action.startswith("lnk_code_"):
        key = action.replace("lnk_code_", "")
        msg = bot.send_message(call.message.chat.id, f"🔢 أرسل الكود الجديد:")
        bot.register_next_step_handler(msg, partial(admin_update_link_field, link_key=key, field="code"))

    elif action.startswith("lnk_pts_"):
        key = action.replace("lnk_pts_", "")
        msg = bot.send_message(call.message.chat.id, f"💎 أرسل عدد النقاط:")
        bot.register_next_step_handler(msg, partial(admin_update_link_pts, link_key=key))

    elif action.startswith("lnk_lar_"):
        key = action.replace("lnk_lar_", "")
        msg = bot.send_message(call.message.chat.id, "🏷️ أرسل الاسم العربي الجديد:")
        bot.register_next_step_handler(msg, partial(admin_update_link_field, link_key=key, field="label_ar"))

    elif action.startswith("lnk_len_"):
        key = action.replace("lnk_len_", "")
        msg = bot.send_message(call.message.chat.id, "🏷️ Send new English label:")
        bot.register_next_step_handler(msg, partial(admin_update_link_field, link_key=key, field="label_en"))

    elif action == "adm_rewards":
        rewards = load_rewards_from_db()
        markup  = types.InlineKeyboardMarkup(row_width=1)
        for key, info in rewards.items():
            markup.add(types.InlineKeyboardButton(
                f"✏️ {info['title_ar']} ┃ {info['points']}نقطة",
                callback_data=f"rwd_edit_{key}"))
        markup.add(types.InlineKeyboardButton("➕ إضافة مكافأة", callback_data="rwd_add"))
        bot.send_message(call.message.chat.id,
            "━━━━━━━━━━━━━━━━━━━━━━\n🎁 **إدارة المكافآت**\n━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=markup, parse_mode="Markdown")

    elif action == "rwd_add":
        msg = bot.send_message(call.message.chat.id,
            "➕ **إضافة مكافأة**\n\n4 أسطر:\n"
            "1. مفتاح (pubg/ff/balance)\n2. نقاط\n3. اسم عربي\n4. اسم إنجليزي",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, admin_add_reward_handler)

    elif action.startswith("rwd_edit_"):
        key     = action.replace("rwd_edit_", "")
        rewards = load_rewards_from_db()
        info    = rewards.get(key, {})
        markup  = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💰 تعديل السعر",   callback_data=f"editprice_{key}"),
            types.InlineKeyboardButton("🗑️ حذف",          callback_data=f"rwd_del_{key}"),
            types.InlineKeyboardButton("🔙 رجوع",           callback_data="adm_rewards"),
        )
        bot.send_message(call.message.chat.id,
            f"🎁 **{info.get('title_ar','؟')}**\n💰 السعر: **{info.get('points','؟')}** نقطة",
            reply_markup=markup, parse_mode="Markdown")

    elif action.startswith("rwd_del_"):
        key = action.replace("rwd_del_", "")
        rewards = load_rewards_from_db()
        info    = rewards.get(key, {})
        delete_reward_from_db(key)
        bot.send_message(call.message.chat.id,
            f"🗑️ تم حذف: **{info.get('title_ar','؟')}**", parse_mode="Markdown")

    elif action.startswith("editprice_"):
        key     = action.replace("editprice_", "")
        rewards = load_rewards_from_db()
        info    = rewards.get(key, {})
        msg = bot.send_message(call.message.chat.id,
            f"💰 **{info.get('title_ar','؟')}**\n"
            f"السعر الحالي: **{info.get('points','؟')}** نقطة\n\n"
            f"أرسل السعر الجديد (رقم فقط):",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, admin_save_new_price, key)

    elif action == "adm_change_channel":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔢 تغيير ID",   callback_data="adm_ch_id"),
            types.InlineKeyboardButton("🔗 تغيير Link", callback_data="adm_ch_link"),
        )
        bot.send_message(call.message.chat.id,
            f"📺 **القناة الحالية**\n🆔 `{get_channel_id()}`\n🔗 {get_channel_link()}",
            reply_markup=markup, parse_mode="Markdown")

    elif action == "adm_ch_id":
        msg = bot.send_message(call.message.chat.id, "🔢 أرسل Channel ID الجديد:")
        bot.register_next_step_handler(msg, admin_save_channel_id)

    elif action == "adm_ch_link":
        msg = bot.send_message(call.message.chat.id, "🔗 أرسل رابط القناة الجديد:")
        bot.register_next_step_handler(msg, admin_save_channel_link)

    elif action == "adm_search_user":
        msg = bot.send_message(call.message.chat.id, "🔍 أرسل آيدي المستخدم:")
        bot.register_next_step_handler(msg, admin_search_user)

    elif action == "adm_add_points":
        msg = bot.send_message(call.message.chat.id,
            "➕ أرسل: `آيدي نقاط`\nمثال: `123456 50`", parse_mode="Markdown")
        bot.register_next_step_handler(msg, admin_add_points_handler)

    elif action == "adm_remove_points":
        msg = bot.send_message(call.message.chat.id,
            "➖ أرسل: `آيدي نقاط`\nمثال: `123456 20`", parse_mode="Markdown")
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

    elif action == "adm_wallet":
        current = get_setting('wallet_address') or WALLET_ADDRESS
        msg = bot.send_message(call.message.chat.id,
            f"💵 **عنوان المحفظة الحالي:**\n`{current}`\n\n"
            f"أرسل العنوان الجديد:",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, admin_save_wallet_address)


        msg = bot.send_message(call.message.chat.id, "📢 أرسل نص الإذاعة:")
        bot.register_next_step_handler(msg, admin_execute_broadcast)

    elif action == "adm_stickers":
        markup = types.InlineKeyboardMarkup(row_width=1)
        sticker_keys = {
            "welcome": "🎉 ستيكر الترحيب",
            "tasks":   "📋 ستيكر المهمات",
            "success": "✅ ستيكر النجاح",
            "wait":    "⏳ ستيكر الانتظار",
            "reward":  "🎁 ستيكر المكافأة",
        }
        for key, label in sticker_keys.items():
            current = get_setting(f"sticker_{key}") or "غير محدد"
            status  = "✅" if current and current != "غير محدد" else "❌"
            markup.add(types.InlineKeyboardButton(
                f"{status} {label}", callback_data=f"stk_set_{key}"))
        bot.send_message(call.message.chat.id,
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎭 **إدارة الستيكرات**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "✅ = محدد  |  ❌ = غير محدد\n\n"
            "**كيف تضيف ستيكر؟**\n"
            "اضغط على الستيكر المطلوب\n"
            "ثم ابعت الستيكر في الشات 👇",
            reply_markup=markup, parse_mode="Markdown")

    elif action.startswith("stk_set_"):
        key = action.replace("stk_set_", "")
        labels = {
            "welcome": "الترحيب", "tasks": "المهمات",
            "success": "النجاح",  "wait":  "الانتظار", "reward": "المكافأة"
        }
        msg = bot.send_message(call.message.chat.id,
            f"🎭 ابعت ستيكر **{labels.get(key, key)}** الآن:\n"
            f"(ابعت الستيكر كستيكر مش صورة)",
            parse_mode="Markdown")
        bot.register_next_step_handler(msg, partial(admin_save_sticker, sticker_key=key))

    elif action.startswith("req-"):
        parts   = action.split("-")
        status  = parts[1]
        req_id  = int(parts[2])
        user_id = int(parts[3])
        final   = "done" if status == "done" else "rejected"
        update_request_status(req_id, final)
        if final == "done":
            try:
                bot.send_message(user_id,
                    "━━━━━━━━━━━━━━━━━━━━━━\n🎉 **تم الشحن!**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "✅ تم تنفيذ طلبك بنجاح 🎊", parse_mode="Markdown")
            except Exception:
                pass
            bot.edit_message_text(f"✅ الطلب #{req_id} — تم التنفيذ",
                call.message.chat.id, call.message.message_id)
        else:
            try:
                bot.send_message(user_id,
                    "❌ **تم رفض طلبك**\nراجع الدعم الفني.", parse_mode="Markdown")
            except Exception:
                pass
            bot.edit_message_text(f"❌ الطلب #{req_id} — تم الرفض",
                call.message.chat.id, call.message.message_id)

# ── Input Handlers ────────────────────────────────────────────────── #

def admin_add_link_handler(message):
    try:
        lines = message.text.strip().split("\n")
        if len(lines) < 6:
            bot.send_message(message.chat.id, "❌ يجب إرسال 6 أسطر.")
            return
        key, url, code = lines[0].strip(), lines[1].strip(), lines[2].strip()
        pts, lar, len_ = int(lines[3].strip()), lines[4].strip(), lines[5].strip()
        if code.upper() == "NONE":
            code = ""
        add_link_to_db(key, url, code, pts, lar, len_)
        bot.send_message(message.chat.id, f"✅ تم إضافة: **{lar}**", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطأ: {e}")

def admin_update_link_field(message, link_key, field):
    update_link_in_db(link_key, field, message.text.strip())
    bot.send_message(message.chat.id, "✅ تم التحديث!")

def admin_update_link_pts(message, link_key):
    try:
        pts = int(message.text.strip())
        update_link_in_db(link_key, "points", pts)
        bot.send_message(message.chat.id, f"✅ تم تحديث النقاط إلى **{pts}**.", parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل رقماً فقط.")

def admin_add_reward_handler(message):
    try:
        lines = message.text.strip().split("\n")
        if len(lines) < 4:
            bot.send_message(message.chat.id, "❌ يجب إرسال 4 أسطر.")
            return
        key, pts, tar, ten = lines[0].strip(), int(lines[1].strip()), lines[2].strip(), lines[3].strip()
        add_reward_to_db(key, pts, tar, ten)
        bot.send_message(message.chat.id, f"✅ تم إضافة: **{tar}**", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطأ: {e}")

def admin_save_new_price(message, reward_key):
    try:
        new_points = int(message.text.strip())
        if new_points < 0:
            bot.send_message(message.chat.id, "❌ لا يمكن سعر سالب.")
            return
        update_reward_price_in_db(reward_key, new_points)
        rewards = load_rewards_from_db()
        info    = rewards.get(reward_key, {})
        bot.send_message(message.chat.id,
            f"✅ تم!\n**{info.get('title_ar','؟')}** → **{new_points}** نقطة",
            parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل رقماً فقط.")

def admin_save_channel_id(message):
    try:
        new_id = int(message.text.strip())
        set_setting('channel_id', new_id)
        bot.send_message(message.chat.id, f"✅ تم حفظ ID: `{new_id}`", parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "❌ يجب إرسال رقم صحيح.")

def admin_save_channel_link(message):
    new_link = message.text.strip()
    if not new_link.startswith("https://"):
        bot.send_message(message.chat.id, "❌ الرابط يبدأ بـ https://")
        return
    set_setting('channel_link', new_link)
    bot.send_message(message.chat.id, f"✅ تم حفظ الرابط: {new_link}")

def admin_search_user(message):
    try:
        target_id = int(message.text.strip())
        info = get_user_info(target_id)
        if not info:
            bot.send_message(message.chat.id, "❌ المستخدم غير موجود.")
            return
        uid, uname, fname, pts, banned, lang, ref_by, ref_count, ref_pts, joined, first_task = info
        bot.send_message(message.chat.id,
            f"━━━━━━━━━━━━━━━━━━━━━━\n👤 **معلومات المستخدم**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🆔 `{uid}`\n📝 **{fname}**\n👤 @{uname}\n"
            f"💎 النقاط: **{pts}**\n🌐 اللغة: {lang}\n"
            f"👥 دعوات: {ref_count} (كسب {ref_pts} نقطة)\n"
            f"✅ أول مهمة: {'تم' if first_task else 'لم يكملها بعد'}\n"
            f"🚫 محظور: {'نعم 🔴' if banned else 'لا ✅'}\n📅 {joined}",
            parse_mode="Markdown")
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل آيدي رقمي.")

def admin_add_points_handler(message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            raise ValueError
        target_id, pts = int(parts[0]), int(parts[1])
        update_user_points(target_id, pts)
        new_pts = get_user_points(target_id)
        bot.send_message(message.chat.id,
            f"✅ تمت إضافة **{pts}** نقطة → `{target_id}`\nالرصيد: **{new_pts}**",
            parse_mode="Markdown")
        try:
            bot.send_message(target_id,
                f"🎁 **هدية من الإدارة!**\n+**{pts}** نقطة 🎊\n💎 رصيدك: **{new_pts}**",
                parse_mode="Markdown")
        except Exception:
            pass
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "❌ الصيغة: `آيدي نقاط`", parse_mode="Markdown")

def admin_remove_points_handler(message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            raise ValueError
        target_id, pts = int(parts[0]), int(parts[1])
        update_user_points(target_id, -pts)
        new_pts = get_user_points(target_id)
        bot.send_message(message.chat.id,
            f"✅ تم خصم **{pts}** نقطة من `{target_id}`\nالرصيد: **{new_pts}**",
            parse_mode="Markdown")
    except (ValueError, IndexError):
        bot.send_message(message.chat.id, "❌ الصيغة: `آيدي نقاط`", parse_mode="Markdown")

def admin_ban_user_handler(message):
    try:
        target_id = int(message.text.strip())
        ban_user(target_id)
        bot.send_message(message.chat.id, f"🚫 تم حظر `{target_id}`.", parse_mode="Markdown")
        try:
            bot.send_message(target_id, "🚫 تم إيقاف حسابك.")
        except Exception:
            pass
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل آيدي رقمي.")

def admin_unban_user_handler(message):
    try:
        target_id = int(message.text.strip())
        unban_user(target_id)
        bot.send_message(message.chat.id, f"✅ تم رفع الحظر عن `{target_id}`.", parse_mode="Markdown")
        try:
            bot.send_message(target_id, "✅ **تم رفع الحظر!** يمكنك استخدام البوت 🎉", parse_mode="Markdown")
        except Exception:
            pass
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل آيدي رقمي.")

def admin_get_user_id_for_proof(message):
    try:
        target_id = int(message.text.strip())
        msg = bot.send_message(message.chat.id,
            f"📸 أرسل صورة الإيصال للمستخدم `{target_id}`:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, admin_send_image_proof_to_user, target_id)
    except ValueError:
        bot.send_message(message.chat.id, "❌ أرسل آيدي رقمي.")

def admin_send_image_proof_to_user(message, target_id):
    if message.content_type != 'photo':
        bot.send_message(message.chat.id, "❌ يجب إرسال صورة.")
        return
    file_id = message.photo[-1].file_id
    try:
        bot.send_photo(target_id, file_id,
            caption="🎉 **تم الشحن بنجاح!**\n📸 إيصال الشحن الرسمي 🎊",
            parse_mode="Markdown")
        bot.send_message(message.chat.id, f"✅ تم إرسال الإثبات لـ `{target_id}`.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ فشل: {e}")

def admin_save_sticker(message, sticker_key):
    """حفظ file_id الستيكر"""
    if message.content_type != 'sticker':
        bot.send_message(message.chat.id,
            "❌ يجب إرسال ستيكر وليس صورة أو نص!")
        return
    file_id = message.sticker.file_id
    set_setting(f"sticker_{sticker_key}", file_id)
    labels = {
        "welcome": "الترحيب", "tasks": "المهمات",
        "success": "النجاح",  "wait":  "الانتظار", "reward": "المكافأة"
    }
    bot.send_message(message.chat.id,
        f"✅ تم حفظ ستيكر **{labels.get(sticker_key, sticker_key)}** بنجاح!",
        parse_mode="Markdown")
    # أرسل الستيكر للتأكيد
    try:
        bot.send_sticker(message.chat.id, file_id)
    except Exception:
        pass

def admin_save_wallet_address(message):
    new_addr = message.text.strip()
    set_setting('wallet_address', new_addr)
    bot.send_message(message.chat.id,
        f"✅ تم حفظ عنوان المحفظة:\n`{new_addr}`",
        parse_mode="Markdown")


    broadcast_text = message.text
    users   = get_all_user_ids()
    bot.send_message(message.chat.id,
        f"🔄 جاري الإذاعة لـ **{len(users)}** مستخدم...", parse_mode="Markdown")
    success = failed = 0
    for uid in users:
        try:
            bot.send_message(uid, broadcast_text)
            success += 1
            time.sleep(0.05)
        except Exception:
            failed += 1
    bot.send_message(message.chat.id,
        f"━━━━━━━━━━━━━━━━━━━━━━\n📢 **اكتملت الإذاعة**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ نجح: **{success}**\n❌ فشل: **{failed}**",
        parse_mode="Markdown")

# ================================================================= #
# 13. LAUNCH                                                          #
# ================================================================= #

if __name__ == "__main__":
    init_db()
    print("=" * 52)
    print("🤖 البوت يعمل الآن بنجاح...")
    print("⚙️  /admin — لوحة التحكم الكاملة")
    print("=" * 52)
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

