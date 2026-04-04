import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import re
import time

# إعداد البوت
API_TOKEN = '8171244208:AAEyiSxzLy6SjlS4r4oU48x3eU4feZMzIUk'
bot = telebot.TeleBot(API_TOKEN)

# دالة توليد السكربت بناءً على الدولة المختارة
def get_zaki_script(region_code):
    return f'''
cat <<EOF > zaki_pro.sh
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --quiet
cat <<EOT > config.json
{{
  "inbounds": [{{"port": 8080, "protocol": "vless", "settings": {{"clients": [{{"id": "18102007-0000-4000-8000-000000000000"}}], "decryption": "none"}}, "streamSettings": {{"network": "ws", "wsSettings": {{"path": "/Zaki-Neymar-L-RealMadrid"}}}}}}],
  "outbounds": [{{"protocol": "freedom"}}]
}}
EOT
cat <<EOT > Dockerfile
FROM alpine:latest
RUN apk add --no-cache curl && curl -L -o /v2ray.zip https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip && unzip /v2ray.zip && chmod +x /v2ray && rm /v2ray.zip
COPY config.json /config.json
CMD /v2ray run -config /config.json
EOT
gcloud builds submit --tag gcr.io/\\$GOOGLE_CLOUD_PROJECT/zaki-pro --quiet
gcloud run deploy zaki-server --image gcr.io/\\$GOOGLE_CLOUD_PROJECT/zaki-pro --region {region_code} --port 8080 --cpu 1 --memory 512Mi --allow-unauthenticated --quiet
gcloud run services describe zaki-server --region {region_code} --format='value(status.url)'
EOF
bash zaki_pro.sh
'''

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🌟 أهلاً بك في بوت زاكي برو!\nأرسل رابط 'Open Console' الخاص بالمختبر للبدء.")

@bot.message_handler(func=lambda m: "token=" in m.text)
def handle_lab(message):
    # إنشاء لوحة اختيار الدولة
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("🇧🇪 بلجيكا", callback_data=f"reg_europe-west1_{message.text}"),
               telebot.types.InlineKeyboardButton("🇫🇷 فرنسا", callback_data=f"reg_europe-west9_{message.text}"))
    markup.add(telebot.types.InlineKeyboardButton("🇩🇪 ألمانيا", callback_data=f"reg_europe-west3_{message.text}"),
               telebot.types.InlineKeyboardButton("🇳🇱 هولندا", callback_data=f"reg_europe-west4_{message.text}"))
    
    bot.reply_to(message, "📍 اختر الدولة التي تريد إنشاء السيرفر فيها:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reg_"))
def process_region(call):
    data = call.data.split("_")
    region = data[1]
    url = data[2]
    
    status = bot.edit_message_text(f"⏳ جاري العمل في منطقة {region}...", call.message.chat.id, call.message.message_id)
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # محاكاة متصفح حقيقي
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # استخدام webdriver_manager ليعمل على جيث هوب تلقائياً
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        time.sleep(15)

        # تجاوز زر "J'ai compris" بالذكاء الاصطناعي
        bot.edit_message_text("🔓 جاري تجاوز حماية جوجل...", call.message.chat.id, status.message_id)
        driver.execute_script("document.querySelectorAll('button').forEach(b => { if(b.innerText.includes('compris') || b.innerText.includes('Got it') || b.innerText.includes('موافق')) b.click(); });")
        time.sleep(10)

        # فتح الـ Cloud Shell
        bot.edit_message_text("🐚 فتح الشاشة السوداء...", call.message.chat.id, status.message_id)
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL, Keys.ALT, "t")
        time.sleep(30)

        # لصق السكربت المخصص للدولة
        bot.edit_message_text(f"⌨️ يتم الآن بناء السيرفر في {region}...", call.message.chat.id, status.message_id)
        actions = webdriver.ActionChains(driver)
        actions.send_keys(get_zaki_script(region)).send_keys(Keys.ENTER).perform()

        # الانتظار الاستراتيجي للـ Revision
        time.sleep(190)
        
        content = driver.page_source
        host_match = re.search(r'https://([a-z0-9-.]+\.run\.app)', content)

        if host_match:
            host = host_match.group(1).strip()
            # إنشاء رابط VLESS النهائي
            vless_link = f"vless://18102007-0000-4000-8000-000000000000@{host}:443?encryption=none&security=tls&sni=youtube.com&type=ws&host={host}&path=%2FZaki-Neymar-L-RealMadrid#Zaki_{region}"
            
            bot.send_message(call.message.chat.id, f"✅ **تم إنشاء السيرفر بنجاح!**\n\nالدولة: {region}\n\nالرابط (اضغط للنسخ):\n`{vless_link}`")
            bot.edit_message_text("✨ Revision Done ✅", call.message.chat.id, status.message_id)
        else:
            bot.edit_message_text("❌ فشل استخراج الهوست، حاول مرة أخرى برابط جديد.", call.message.chat.id, status.message_id)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ خطأ: {str(e)}")
    finally:
        driver.quit()

print("--- بوت زاكي العالمي يعمل الآن ---")
bot.infinity_polling()
