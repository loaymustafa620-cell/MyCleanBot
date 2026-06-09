import time
import requests
import threading
import telebot
import logging

# 1. إعدادات السجل (عشان نعرف إيه اللي بيحصل بالظبط لو في خطأ)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 2. إعدادات البوت واللوحة
BOT_TOKEN = "8565993247:AAHd3grcinVcmf_61MJt3Bn7rwPIxpBcXT0"
bot = telebot.TeleBot(BOT_TOKEN)

# 3. بيانات اللوحة (كل تفصيلة صغيرة)
DASHBOARD = {
    "login_url": "https://ivas.tempnum.qzz.io/login",
    "sms_api": "https://ivas.tempnum.qzz.io/portal/sms/received/getsms",
    "user": "lab061449@gmail.com",
    "pass": "0453902350aA",
    "session": requests.Session(), # السيسشن الموحد للحفاظ على تسجيل الدخول
    "is_active": True
}

# 4. وظيفة تسجيل الدخول (بالتفصيل)
def login_to_panel():
    logging.info("بدء محاولة تسجيل الدخول...")
    try:
        login_data = {"email": DASHBOARD["user"], "password": DASHBOARD["pass"]}
        response = DASHBOARD["session"].post(DASHBOARD["login_url"], data=login_data, timeout=10)
        if response.status_code == 200:
            logging.info("تم تسجيل الدخول بنجاح.")
            return True
        else:
            logging.error(f"فشل تسجيل الدخول، كود الموقع: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"خطأ في الاتصال أثناء تسجيل الدخول: {e}")
        return False

# 5. محرك سحب البيانات (بكل تفصيلاته)
def data_engine():
    logging.info("بدء تشغيل محرك البيانات...")
    if not login_to_panel():
        logging.warning("المحرك سيعمل بدون تسجيل دخول حالي!")

    while DASHBOARD["is_active"]:
        try:
            # محاولة السحب
            resp = DASHBOARD["session"].get(DASHBOARD["sms_api"], timeout=10)
            
            if resp.status_code == 200:
                # لو سحبنا بيانات
                logging.info(f"بيانات تم سحبها: {len(resp.text)} حرف")
            elif resp.status_code == 401 or resp.status_code == 403:
                # إعادة تسجيل الدخول في حال انتهت الجلسة
                logging.warning("الجلسة انتهت، إعادة تسجيل الدخول...")
                login_to_panel()
            else:
                logging.error(f"خطأ غير متوقع: {resp.status_code}")
                
        except Exception as e:
            logging.error(f"خطأ في السحب: {e}")
        
        # الانتظار بين كل محاولة (عشان متتحظرش)
        time.sleep(2)

# 6. التشغيل المتوازي
if __name__ == "__main__":
    # تشغيل المحرك في خيط منفصل (عشان ميعطلش البوت)
    threading.Thread(target=data_engine, daemon=True).start()
    
    # تشغيل البوت
    logging.info("البوت بدأ العمل...")
    bot.polling(none_stop=True)

