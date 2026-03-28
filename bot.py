from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = "8594390840:AAEwF-2xPrnuXv7Ldlg7FI1HXegVcGTWKsQ"

user_url = {}  # تخزين الرابط


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📸 تابعنا على إنستغرام", url="https://www.instagram.com/beweble")]
    ]

    await update.message.reply_text(
        "✨ أهلاً بك في MediaX Bot 🔥\n\n"
        "📥 أرسل أي رابط وسأعطيك خيار التحميل\n"
        "🎥 فيديو أو 🎵 موسيقى\n"
        "━━━━━━━━━━━━━━\n"
        "👨‍💻 Programming by Rida Jomaa\n\n"
        "📸 تابعنا على إنستغرام 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- استقبال الرابط ----------------
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    url = update.message.text

    user_url[user_id] = url

    keyboard = [
        [
            InlineKeyboardButton("🎥 فيديو", callback_data="video"),
            InlineKeyboardButton("🎵 موسيقى", callback_data="audio")
        ]
    ]

    await update.message.reply_text(
        "📥 اختر نوع التحميل 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- اختيار النوع ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    url = user_url.get(user_id)

    if not url:
        await query.edit_message_text("❌ أرسل الرابط أولاً")
        return

    mode = query.data

    msg = await query.edit_message_text("⏳ جاري التحميل...")

    try:
        if mode == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': 'video.%(ext)s',
                'merge_output_format': 'mp4'
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if mode == "audio":
            audio_file = os.path.splitext(filename)[0] + ".mp3"
            await query.message.reply_audio(audio=open(audio_file, "rb"))
            os.remove(audio_file)
        else:
            await query.message.reply_video(video=open(filename, "rb"))
            os.remove(filename)

        await msg.edit_text("✅ تم التحميل بنجاح 🔥")

        # تنظيف
        user_url.pop(user_id, None)

    except Exception as e:
        await msg.edit_text("❌ صار خطأ بالرابط")
        print(e)


# ---------------- تشغيل البوت ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
app.add_handler(CallbackQueryHandler(button))

print("Bot is running...")
app.run_polling()
