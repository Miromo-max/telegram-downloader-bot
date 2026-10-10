import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot 24/7 ishlamoqda!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# --- 1. WEB SERVER (Render uchun) ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot 24/7 ishlamoqda!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()


# --- 2. TILLAR VA MATNLAR LUG'ATI ---
TEXTS = {
    'uz': {
        'welcome': "Xush kelibsiz! Musiqa yoki video havolasini (link) yuboring:",
        'downloading': "Yuklab olinmoqda, kuting...",
        'lang_saved': "Til muvaffaqiyatli O'zbek tiliga o'zgartirildi! 🇺🇿"
    },
    'ru': {
        'welcome': "Добро пожаловать! Отправьте ссылку на музыку или видео:",
        'downloading': "Скачивается, подождите...",
        'lang_saved': "Язык успешно изменен на Русский! 🇷🇺"
    },
    'en': {
        'welcome': "Welcome! Send a link to music or video:",
        'downloading': "Downloading, please wait...",
        'lang_saved': "Language successfully set to English! 🇬🇧"
    }
}

# Foydalanuvchilar tanlagan tilni saqlash xotirasi
user_languages = {}


# --- 3. BOT BUYRUKLARI (HANDLERS) ---

# /start bosilganda til tanlash tugmalarini ko'rsatish
async def start(update: Update, context):
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='lang_uz'),
            InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Iltimos, tilni tanlang / Пожалуйста, выберите язык / Please select a language:",
        reply_markup=reply_markup
    )

# Tugma bosilganda tilni saqlash va salomlashish
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data.startswith('lang_'):
        lang = query.data.split('_')[1]  # 'uz', 'ru' yoki 'en'
        user_languages[user_id] = lang   # Foydalanuvchi tilini xotiraga yozamiz
        
        # Tanlangan dilda javob berish
        await query.edit_message_text(text=TEXTS[lang]['welcome'])

# Foydalanuvchi havola (link) yuborganda
async def handle_message(update: Update, context):
    user_id = update.effective_user.id
    # Agar foydalanuvchi til tanlamagan bo'lsa, avtomatik 'uz' qilamiz
    lang = user_languages.get(user_id, 'uz')
    
    # Botingizning yuklab olish kodi shu yerda bo'ladi:
    await update.message.reply_text(TEXTS[lang]['downloading'])
    
    # ... Bu yerda yt_dlp yoki boshqa yuklash kodingiz davom etadi ...


# --- 4. BOTNI ISHGA TUSHIRISH ---
TOKEN = '8914594418:AAHygV6YT1pGb09x2eBM1LkC8zh6BQ_j7gs' # O'zingizning tokeningiz

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == '__main__':
    main()
