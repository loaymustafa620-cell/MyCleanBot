import time
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import threading

BOT_TOKEN = "8877226268:AAFYJFK0FjzvqJl-XnUg4RPsGT6VvyjdsVE"
ADMIN_ID = 6320384889  # الآي دي الحقيقي بتاعك يا لؤي
CHANNEL_USERNAME = "@MloayM"  # معرف قناتك الأساسية للاشتراك الإجباري
LOG_GROUP_ID = -1003962030743  # آي دي قناة/جروب اللوجات والتقارير الخاصة بك

bot = telebot.TeleBot(BOT_TOKEN)

# دالة فحص الاشتراك الإجباري
def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        return True

# دالة سحب الأرقام من الموقع المجاني بشكل عشوائي متجدد
def get_free_numbers():
    url = "https://anonymsms.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    numbers_list = []
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if "/number/" in href:
                    num = href.split("/number/")[-1].strip("/")
                    if num and num.isdigit() and len(num) > 7:
                        if num not in numbers_list:
                            numbers_list.append(num)
        # خلط الأرقام وإرجاع 6 أرقام مختلفة في كل مرة يتم تحديث البوت
        import random
        random.shuffle(numbers_list)
        return numbers_list[:6]
    except Exception:
        return []

# دالة قراءة آخر رسالة قادمة للرقم
def get_latest_sms(phone_number):
    url = f"https://anonymsms.com/number/{phone_number}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            messages = soup.find_all('td', data_title="Message")
            if messages:
                return messages[0].text.strip()
    except Exception:
        pass
    return None

# دالة المراقبة الطويلة وإرسال البيانات لقنواتك
def monitor_free_sms(chat_id, user_name, phone_number):
    bot.send_message(chat_id, f"👀 بدأت العين السحرية بمراقبة الرقم: `+{phone_number}`\nاطلب الكود الآن من تطبيقك، البوت هيفحص الموقع كل 8 ثواني بدون توقف لوصول الكود!", parse_mode="Markdown")
    
    # إرسال تقرير فوري لقناتك الخاصة بالتقارير LOG_GROUP_ID
    try:
        bot.send_message(LOG_GROUP_ID, f"📢 *طلب مراقبة جديد:*\n👤 المستخدم: {user_name}\n🆔 الآي دي: `{chat_id}`\n📱 الرقم المختار: `+{phone_number}`", parse_mode="Markdown")
    except Exception:
        pass

    last_found_msg = ""
    for _ in range(75): # فحص مستمر لمدة 10 دقائق كاملة لحل مشكلة التأخير
        time.sleep(8)
        latest_msg = get_latest_sms(phone_number)
        
        if int(chat_id) == ADMIN_ID: # لو أنت الأدمن، بيظهرلك إشعار فحص داخلي
            print(f"[+] جاري فحص الرسائل للرقم {phone_number}...")

        if latest_msg and latest_msg != last_found_msg:
            # فلترة ذكية للرسالة للتأكد من أنها تحتوي على أكواد
            if any(k in latest_msg.lower() for k in ["code", "otp", "verification", "تأكيد", "رمز", "whatsapp", "telegram", "تليجرام"]):
                bot.send_message(
                    chat_id, 
                    f"🔥 *يا لؤي! الكود وصل الحين على البوت:*\n\n"
                    f"📱 الرقم المستهدف: `+{phone_number}`\n"
                    f"✉️ نص الرسالة بالكامل:\n`{latest_msg}`", 
                    parse_mode="Markdown"
                )
                # إرسال إشعار بنجاح العملية لقناتك السريّة
                try:
                    bot.send_message(LOG_GROUP_ID, f"✅ *تم صيد الكود بنجاح!*\n👤 المستخدم: {user_name}\n📱 الرقم: `+{phone_number}`\n✉️ الرسالة: `{latest_msg}`", parse_mode="Markdown")
                except Exception:
                    pass
                return
            last_found_msg = latest_msg
            
    bot.send_message(chat_id, f"⏱️ انتهت الـ 10 دقائق ولم يظهر كود جديد مناسب على الموقع للرقم `+{phone_number}`.\n\n💡 نصيحة: جرب تطلب الكود في تطبيقك (رسالة نصية مجدداً) أو اختر رقماً آخر واضغط /start لتحديث القائمة.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # تحقق الاشتراك الإجباري بقناتك @MloayM
    if not check_sub(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="📢 اشترك في القناة أولاً", url=f"https://t.me/MloayM"))
        markup.add(types.InlineKeyboardButton(text="🔄 تأكيد الاشتراك", callback_data="check_again"))
        bot.reply_to(message, f"⚠️ أهلاً بك يا غالي! لتفعيل البوت وحفظ حقوق المطور لؤي، يرجى الاشتراك بقناتنا الرسمية أولاً ثم اضغط تأكيد.", reply_markup=markup)
        return

    msg = bot.reply_to(message, "🔄 جاري الاتصال بقاعدة البيانات وسحب أرقام مجانية متجددة الآن...")
    free_nums = get_free_numbers()
    
    if free_nums:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for num in free_nums:
            markup.add(types.InlineKeyboardButton(text=f"📱 +{num} [شغال وعام]", callback_data=f"show_{num}"))
        
        # لوحة التحكم الخاصة بك كمالك ومطور للبوت
        if message.from_user.id == ADMIN_ID:
            markup.add(types.InlineKeyboardButton(text="⚙️ لوحة تحكم لؤي المطور", callback_data="admin_panel"))

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text="🎯 *إليك الأرقام المجانية المتاحة حالياً للتجربة:*\n\n(اختر الرقم واكتبه في تطبيقك، ثم اضغط على زر المراقبة وسيقوم البوت بسحب الكود تلقائياً!)",
            parse_mode="Markdown",
            reply_markup=markup
        )
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="❌ السيرفر مضغوط حالياً بسبب كثرة الطلبات. أرسل /start مرة أخرى.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name

    if call.data == "check_again":
        if check_sub(user_id):
            bot.answer_callback_query(call.id, text="✅ تم التحقق بنجاح! عيش المتعة.")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_welcome(call.message)
        else:
            bot.answer_callback_query(call.id, text="❌ أنت غير مشترك في قناة @MloayM حتى الآن!", show_alert=True)

    elif call.data.startswith('show_'):
        phone_number = call.data.split('_')[1]
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔄 ابدأ سحب ومراقبة الكود (10 دقائق)", callback_data=f"trackfree_{phone_number}"))
        bot.send_message(call.message.chat.id, f"📱 الرقم المختار: `+{phone_number}`\n\n1️⃣ حطه في التطبيق اللي بتفعله.\n2️⃣ اضغط على الزرار بالأسفل فوراً لتشغيل المراقبة الطويلة وسحب الـ OTP!", parse_mode="Markdown", reply_markup=markup)

    elif call.data.startswith('trackfree_'):
        phone_number = call.data.split('_')[1]
        bot.answer_callback_query(call.id, text="🎯 تم تشغيل العين السحرية للمراقبة...")
        threading.Thread(target=monitor_free_sms, args=(call.message.chat.id, user_name, phone_number)).start()

    elif call.data == "admin_panel" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="📊 تقرير حالة السيرفرات قنواتك", callback_data="admin_stats"))
        bot.send_message(call.message.chat.id, "👑 مرحباً بك يا لؤي في لوحة تحكم المطور المالك الإدارية:", reply_markup=markup)

    elif call.data == "admin_stats" and user_id == ADMIN_ID:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"📊 *إحصائيات الإدارة:*\n\n• قناة الاشتراك الإجباري: @MloayM\n• قناة استقبال التقارير: متصلة ونشطة\n• نوع السحب الحالي: مجاني عام (متجدد تلقائياً)")

if __name__ == "__main__":
    print("[*] البوت جاهز ومربوط بقنواتك رسميًا يا لؤي! شغل الحين وعيش الاكشن.")
    bot.remove_webhook()
    bot.infinity_polling()

