import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Bu yerga BotFather'dan olgan tokeningizni yozing
TOKEN = '8914594418:AAHygV6YTipGbO9x2eBW1LkC8zh6BQ_j7gs'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Menga Instagram, TikTok yoki YouTube havolasini (link) yuboring, "
        "men uni video yoki audio ko'rinishida yuklab beraman."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # Havolani to'g'riligini tekshirish
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("Iltimos, to'g'ri havola (link) yuboring!")
        return

    # Havolani vaqtincha xotirada saqlaymiz
    context.user_data['last_url'] = url

    # Format tanlash tugmalari
    keyboard = [
        [
            InlineKeyboardButton("🎬 Video", callback_data="dl_video"),
            InlineKeyboardButton("🎵 Audio", callback_data="dl_audio")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Nimani yuklab olmoqchisiz? Tanlang:",
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    download_type = query.data
    url = context.user_data.get('last_url')

    if not url:
        await query.edit_message_text("Xatolik: Havola topilmadi. Qaytadan link yuboring.")
        return

    await query.edit_message_text("Fayl yuklab olinmoqda, kuting...")

    try:
        out_pattern = f"download_{query.from_user.id}.%(ext)s"

        # FFmpeg talab qilmaydigan sozlamalar
        if download_type == "dl_video":
            ydl_opts = {
                'format': 'b[ext=mp4]/best[ext=mp4]/best',
                'outtmpl': out_pattern,
                'quiet': True
            }
        else:  # dl_audio
            ydl_opts = {
                'format': 'ba/best',
                'outtmpl': out_pattern,
                'quiet': True
            }

        # Faylni yuklab olish
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Telegramga yuborish
        await query.message.reply_text("Fayl tayyor! Yuborilmoqda...")
        with open(filename, 'rb') as file:
            if download_type == "dl_video":
                await context.bot.send_video(chat_id=query.message.chat_id, video=file)
            else:
                await context.bot.send_audio(chat_id=query.message.chat_id, audio=file)

        # Vaqtinchalik faylni o'chirish
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        await query.message.reply_text(f"Xatolik yuz berdi: {str(e)}")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()