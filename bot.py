from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os

TOKEN = "8594390840:AAEwF-2xPrnuXv7Ldlg7FI1HXegVcGTWKsQ"


# ---------------- START MESSAGE ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً فيك!\n\n"
        "📥 أنا بوت تحميل فيديو + صوت\n"
        "🎥 ابعت أي رابط وأنا بحمّله إلك\n\n"
        "⚙️ تم برمجة هذا البوت خصيصاً لك\n"
        "📸 تابعنا على إنستغرام: https://www.instagram.com/beweble"
    )


# ---------------- DOWNLOAD FUNCTION ----------------
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("⏳ عم بحمّل الملف...")

    try:
        # إعدادات التحميل
        ydl_opts = {
            'outtmpl': 'file.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # إرسال الفيديو
        await update.message.reply_video(video=open(filename, 'rb'))

        os.remove(filename)

    except Exception as e:
        try:
            # لو فشل الفيديو نحاول صوت
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = "audio.mp3"

            await update.message.reply_audio(audio=open(filename, 'rb'))

            os.remove(filename)

        except Exception:
            await update.message.reply_text("❌ الرابط غير مدعوم أو في مشكلة")


# ---------------- MAIN APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

print("Bot is running...")
app.run_polling()
