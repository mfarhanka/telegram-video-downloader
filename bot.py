import os
import yt_dlp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me an Instagram video link and I'll download it for you!")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "instagram.com" not in url:
        await update.message.reply_text("❌ Please send a valid Instagram link.")
        return

    # Step 1: Acknowledge
    progress_msg = await update.message.reply_text("🔍 Checking link...")

    try:
        # Step 2: Downloading
        await progress_msg.edit_text("⬇️ Downloading video, please wait...")

        ydl_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "quiet": True,
            "merge_output_format": "mp4",
            # Limit file size to 50MB (Telegram's limit)
            "max_filesize": 50 * 1024 * 1024,
        }

        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            # Ensure .mp4 extension
            if not file_path.endswith(".mp4"):
                file_path = os.path.splitext(file_path)[0] + ".mp4"

        # Check if file exists
        if not os.path.exists(file_path):
            await progress_msg.edit_text("❌ Download failed. File not found.")
            return

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:
            os.remove(file_path)
            await progress_msg.edit_text("❌ Video is too large to send (max 50MB).")
            return

        # Step 3: Sending
        await progress_msg.edit_text(f"📤 Sending video ({round(file_size / 1024 / 1024, 1)}MB)...")

        with open(file_path, "rb") as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="✅ Here is your video!",
                read_timeout=300,
                write_timeout=300,
                connect_timeout=300,
            )

        # Step 4: Done
        await progress_msg.edit_text("✅ Done!")

        # Cleanup
        os.remove(file_path)

    except Exception as e:
        await progress_msg.edit_text(f"❌ Failed to download video.\n\n`{str(e)}`")
        # Cleanup on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    # Increase timeout for large file uploads
    request = HTTPXRequest(
        read_timeout=300,
        write_timeout=300,
        connect_timeout=300,
        pool_timeout=300,
    )
    app = ApplicationBuilder().token(TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("🤖 Bot is running...")
    app.run_polling()
