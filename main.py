import os
import threading
import yt_dlp
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# --- 1. WEB SERVER (Render 24/7 ishlashi uchun) ---
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


# --- 2. TILLAR VA MATNLAR ---
TEXTS = {
    'uz': {
        'welcome': "Xush kelibsiz! Musiqa yoki video havolasini (link) yuboring:",
        'downloading': "Iltimos kuting, yuklab olinmoqda... ⏳",
        'error': "Xatolik yuz berdi yoki video topilmadi ❌"
    },
    'ru': {
        'welcome': "Добро пожаловать! Отправьте ссылку на музыку или видео:",
        'downloading': "Пожалуйста, подождите, идет скачивание... ⏳",
        'error': "Произошла ошибка или видео не найдено ❌"
    },
    'en': {
        'welcome': "Welcome! Send a link to music or video:",
        'downloading': "Please wait, downloading... ⏳",
        'error': "An error occurred or video was not found ❌"
    }
}

user_languages = {}


# --- 3. BOT FUNKSIYALARI ---
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

async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data.startswith('lang_'):
        lang = query.data.split('_')[1]
        user_languages[user_id] = lang
        await query.edit_message_text(text=TEXTS[lang]['welcome'])

async def handle_message(update: Update, context):
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, 'uz')
    url = update.message.text

    if "http://" in url or "https://" in url:
        status_msg = await update.message.reply_text(TEXTS[lang]['downloading'])
        
        # yt-dlp orqali yuklab olish sozlamalari
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloaded_video.%(ext)s',
            'max_filesize': 50 * 1024 * 1024  # Telegram uchun maksimal 50MB
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            # Videoni Telegram'ga yuklab yuborish
            with open(filename, 'rb') as video_file:
                await update.message.reply_video(video=video_file)
            
            # Server xotirasini tozalash uchun faylni o'chirish
            if os.path.exists(filename):
                os.remove(filename)
                
            await status_msg.delete()
            
        except Exception as e:
            await status_msg.edit_text(TEXTS[lang]['error'])
            if 'filename' in locals() and os.path.exists(filename):
                os.remove(filename)


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
