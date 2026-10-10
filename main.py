import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# --- 1. WEB SERVER (Render uchun 24/7 ishlashi uchun) ---
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
        'downloading': "Iltimos kuting, yuklab olinmoqda... ⏳",
        'lang_saved': "Til O'zbek tiliga o'zgartirildi! 🇺🇿"
    },
    'ru': {
        'welcome': "Добро пожаловать! Отправьте ссылку на музыку или видео:",
        'downloading': "Пожалуйста, подождите, идет скачивание... ⏳",
        'lang_saved': "Язык изменен на Русский! 🇷🇺"
    },
    'en': {
        'welcome': "Welcome! Send a link to music or video:",
        'downloading': "Please wait, downloading... ⏳",
        'lang_saved': "Language changed to English! 🇬🇧"
    }
}

user_languages = {}


# --- 3. BOT BUYRUKLARI ---

# /start bosilganda til tanlash tugmalari
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

# Til tugmasi bosilganda
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data.startswith('lang_'):
        lang = query.data.split('_')[1]
        user_languages[user_id] = lang  # Tanlangan tilni saqlaymiz
        
        await query.edit_message_text(text=TEXTS[lang]['welcome'])

# Foydalanuvchi link yuborganda ishlaydi
async def handle_message(update: Update, context):
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, 'uz')  # Tanlangan tilni olamiz (odatiy uz)
    text = update.message.text

    # Faqat link bo'lsa ishlaydi (http yoki https bo'lsa)
    if "http://" in text or "https://" in text:
        # Tanlangan tildagi "kuting" matnini yuboradi
        await update.message.reply_text(TEXTS[lang]['downloading'])
        
        # --- BU YERGA YUKLAB OLISH (yt-dlp) KODINGIZNI QO'SHASIZ ---
    else:
        # Link bo'lmasa, e'tiborsiz qoldiradi yoki havola yuborishni so'raydi
        pass


# --- 4. BOTNI ISHGA TUSHIRISH ---
TOKEN = '8914594418:AAHygV6YTipGbO9x2eBW1LkC8zh6BQ_j7gs'

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == '__main__':
    main()
