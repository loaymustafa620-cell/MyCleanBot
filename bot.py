import time
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import threading
import random  # تم إضافة المكتبة الناقصة هنا

BOT_TOKEN = "8877226268:AAFYJFK0FjzvqJl-XnUg4RPsGT6VvyjdsVE"
CHANNEL_USERNAME = "MloayM"  # اسم قناتك بدون الـ @ لتفادي الأخطاء في الرابط

bot = telebot.TeleBot(BOT_TOKEN)

# Funkcija za provjeru pretplate
def check_sub(user_id):
    try:
        member = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception:
        return True

# دالة جلب الرسائل من الموقع (تم إضافتها لأنها كانت ناقصة في الكود)
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

# Funkcija za dobivanje besplatnih brojeva
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
            random.shuffle(numbers_list)
            return numbers_list[:6]
    except Exception:
        return []

# Funkcija za praćenje poruka
def monitor_free_sms(chat_id, user_name, phone_number):
    bot.send_message(chat_id, f"👀 Počeo sam praćenje broja: `+{phone_number}`\nZatražite kod u svojoj aplikaciji, bot će provjeriti sajt svakih 8 sekundi.")
    
    last_found_msg = ""  # تم تعريف المتغير هنا لحل مشكلة الـ NameError
    
    for _ in range(75):
        time.sleep(8)
        latest_msg = get_latest_sms(phone_number)
        if latest_msg and latest_msg != last_found_msg:
            if any(k in latest_msg.lower() for k in ["code", "otp", "verification", "tvrđenie", "kôd", "whatsapp", "telegram", "teliigrâm"]):
                bot.send_message(chat_id, f"🔥 *Kod je stigao:*\n\n📱 Broj: `+{phone_number}`\n✉️ Poruka:\n`{latest_msg}`", parse_mode="Markdown")
                return
            last_found_msg = latest_msg

    bot.send_message(chat_id, f"⏱️ Vrijeme za praćenje isteklo. Zatražite kod ponovo ili odaberite drugi broj.")

# Funkcija za start poruku
def send_welcome(message):
    if not check_sub(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="📢 Pretplatite se", url=f"https://t.me/{CHANNEL_USERNAME}"))
        markup.add(types.InlineKeyboardButton(text="🔄 Provjeri pretplatu", callback_data="check_again"))
        bot.reply_to(message, f"⚠️ Da biste koristili bota, pretplatite se na naš kanal.", reply_markup=markup)
        return
    
    free_nums = get_free_numbers()
    if free_nums:
        markup = types.InlineKeyboardMarkup(row_width=1)
        for num in free_nums:
            markup.add(types.InlineKeyboardButton(text=f"📱 +{num}", callback_data=f"show_{num}"))
        bot.reply_to(message, "🎯 *Izaberite broj za praćenje:*", reply_markup=markup)
    else:
        bot.reply_to(message, "❌ Nema dostupnih brojeva. Pokušajte kasnije.")

# Funkcija za obradu callback-a
def handle_callbacks(call):
    if call.data == "check_again":
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, text="✅ Hvala vam!")
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_welcome(call.message)
        else:
            bot.answer_callback_query(call.id, text="❌ Niste se pretplatili!", show_alert=True)
            
    elif call.data.startswith('show_'):
        phone_number = call.data.split('_')[1]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="🔄 Počni praćenje (10 minuta)", callback_data=f"trackfree_{phone_number}"))
        bot.send_message(call.message.chat.id, f"📱 Izabrani broj: `+{phone_number}`\n\n1️⃣ Unesite broj u aplikaciju.\n2️⃣ Kliknite na gumb za praćenje.", reply_markup=markup)

    elif call.data.startswith('trackfree_'):
        phone_number = call.data.split('_')[1]
        threading.Thread(target=monitor_free_sms, args=(call.message.chat.id, call.from_user.first_name, phone_number)).start()

# Glavni dio koda
@bot.message_handler(commands=['start'])
def start_command(message):
    send_welcome(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    handle_callbacks(call)

if __name__ == "__main__":
    print("[*] Bot je spreman!")
    bot.remove_webhook()
    bot.infinity_polling()

