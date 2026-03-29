from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters, CallbackContext
import yt_dlp
import os
import json
from datetime import datetime

TOKEN = "8594390840:AAFaDEXJ8B0K1mmJ87X7bIeEwsc5rcJ4aXE"

user_url = {}

try:
    with open("users.json", "r") as f:
        users = json.load(f)
except:
    users = {}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# ---------------- START ----------------
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = str(user.id)

    users[user_id] = {
        "username": user.username,
        "name": user.first_name,
        "time": str(datetime.now())
    }
    save_users()

    keyboard = [
        [InlineKeyboardButton("📸 Instagram", url="https://www.instagram.com/beweble")]
    ]

    update.message.reply_text(
        "✨ Welcome to MediaX Bot 🔥\n\nSend a link to download 🎥 / 🎵\n\n👨‍💻 Developed by Rida Jomaa",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- DOWNLOAD ----------------
def download(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    url = update.message.text

    user_url[user_id] = url

    keyboard = [
        [
            InlineKeyboardButton("🎥 Video", callback_data="video"),
            InlineKeyboardButton("🎵 Audio", callback_data="audio")
        ]
    ]

    update.message.reply_text(
        "Choose type:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- BUTTON ----------------
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    user_id = query.from_user.id
    url = user_url.get(user_id)

    if not url:
        query.edit_message_text("Send link first ❌")
        return

    mode = query.data
    msg = query.edit_message_text("Downloading... ⏳")

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
            with open(audio_file, "rb") as f:
                query.message.reply_audio(audio=f)
            os.remove(audio_file)
        else:
            with open(filename, "rb") as f:
                query.message.reply_video(video=f)
            os.remove(filename)

        query.edit_message_text("Done ✅")
        user_url.pop(user_id, None)

    except Exception as e:
        query.edit_message_text("Error ❌")
        print(e)

# ---------------- MAIN ----------------
def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
