from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = "8594390840:AAFUyvPcd945sLe-t9C3_QLa4W6cF20is9Y"

user_mode = {}  # حفظ اختيار المستخدم


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎥 تحميل فيديو", callback_data="video")],
        [InlineKeyboardButton("🎵 تحميل موسيقى", callback_data="audio")]
    ]

    await update.message.reply_text(
        "✨ أهلاً بك في أقوى بوت تحميل 🔥\n\n"
        "📥 اختر نوع التحميل الذي تريده:\n"
        "━━━━━━━━━━━━━━\n"
        "⚙️ تم برمجة هذا البوت بواسطة:\n"
        "👨‍💻 Rida Jomaa\n"
        "━━━━━━━━━━━━━━\n"
        "📸 تابعنا على إنستغرام: https://www.instagram.com/beweble",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- BUTTONS ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_mode[query.from_user.id] = query.data

    if query.data == "video":
        await query.edit_message_text("🎥 تمام! ابعت الرابط وأنا بحمّل الفيديو 🔥")
    else:
        await query.edit_message_text("🎵 تمام! ابعت الرابط وأنا بحمّل الموسيقى 🔥")


# ---------------- DOWNLOAD ----------------
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.message.from_user.id
    mode = user_mode.get(user_id, "video")

    msg = await update.message.reply_text("⏳ جاري التحميل... انتظر قليلاً 🔥")

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

        # إرسال الملف
        if mode == "audio":
            audio_file = filename.replace(".webm", ".mp3")
            await update.message.reply_audio(audio=open(audio_file, "rb"))
            os.remove(audio_file)
        else:
            await update.message.reply_video(video=open(filename, "rb"))
            os.remove(filename)

        await msg.edit_text("✅ تم التحميل بنجاح 🔥")

    except Exception:
        await msg.edit_text("❌ الرابط غير مدعوم أو في مشكلة")


# ---------------- MAIN APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot is running...")
app.run_polling()
