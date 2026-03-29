from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp
import os
import json
from datetime import datetime
from flask import Flask, request
import asyncio

# ---------------- TOKEN ----------------
TOKEN = "8594390840:AAHBJFt8rXamY6UCWQHUuVWLKNBEIBD9EOw"

# ---------------- URL (Render link) ----------------
URL = "https://telegram-bot-dj07.onrender.com"

user_url = {}

# ---------------- users storage ----------------
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except:
    users = {}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# ---------------- Flask ----------------
app = Flask(__name__)

# ---------------- Telegram App ----------------
application = ApplicationBuilder().token(TOKEN).build()

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = str(user.id)

    users[user_id] = {
        "username": user.username,
        "name": user.first_name,
        "time": str(datetime.now())
    }
    save_users()

    keyboard = [
        [InlineKeyboardButton("📸 تابعنا على إنستغرام", url="https://www.instagram.com/beweble")]
    ]

    await update.message.reply_text(
        "✨ أهلاً بك في MediaX Bot 🔥\n\n"
        "📥 أرسل أي رابط وسأعطيك خيار التحميل\n"
        "🎥 فيديو أو 🎵 موسيقى",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- download ----------------
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

# ---------------- button ----------------
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
        user_url.pop(user_id, None)

    except Exception as e:
        await msg.edit_text("❌ صار خطأ بالرابط")
        print(e)

# ---------------- handlers ----------------
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
application.add_handler(CallbackQueryHandler(button))

# ---------------- webhook route ----------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# ---------------- home ----------------
@app.route("/")
def home():
    return "Bot is running!"

# ---------------- SET WEBHOOK ----------------
async def set_webhook():
    await application.bot.set_webhook(url=f"{URL}/{TOKEN}")

# ---------------- RUN ----------------
if __name__ == "__main__":
    asyncio.run(set_webhook())
    print("Webhook set!")
    app.run(host="0.0.0.0", port=10000)
