import os
import yt_dlp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def ydl_progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "N/A").strip()
        speed = d.get("_speed_str", "N/A").strip()
        eta = d.get("_eta_str", "N/A").strip()
        print(f"\r⬇️  Downloading... {percent} | Speed: {speed} | ETA: {eta}", end="", flush=True)
    elif d["status"] == "finished":
        print(f"\n✅ Download complete: {d['filename']}")
    elif d["status"] == "error":
        print(f"\n❌ Download error: {d.get('error', 'Unknown error')}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me an Instagram video link and I'll download it for you!")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user = update.message.from_user

    if "instagram.com" not in url:
        await update.message.reply_text("❌ Please send a valid Instagram link.")
        return

    print(f"\n{'='*50}")
    print(f"👤 User: {user.first_name} (@{user.username}) | ID: {user.id}")
    print(f"🔗 URL: {url}")
    print(f"{'='*50}")

    # Step 1: Acknowledge
    progress_msg = await update.message.reply_text("🔍 Checking link...")
    print("🔍 Checking link...")

    try:
        # Step 2: Downloading
        await progress_msg.edit_text("⬇️ Downloading video, please wait...")
        print("⬇️  Starting download...")

        ydl_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "quiet": True,
            "merge_output_format": "mp4",
            "max_filesize": 50 * 1024 * 1024,
            "progress_hooks": [ydl_progress_hook],
        }

        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if not file_path.endswith(".mp4"):
                file_path = os.path.splitext(file_path)[0] + ".mp4"

        # Check if file exists
        if not os.path.exists(file_path):
            await progress_msg.edit_text("❌ Download failed. File not found.")
            print("❌ File not found after download.")
            return

        # Check file size
        file_size = os.path.getsize(file_path)
        file_size_mb = round(file_size / 1024 / 1024, 1)
        print(f"📦 File size: {file_size_mb}MB")

        if file_size > 50 * 1024 * 1024:
            os.remove(file_path)
            await progress_msg.edit_text("❌ Video is too large to send (max 50MB).")
            print("❌ File too large, removed.")
            return

        # Step 3: Sending
        await progress_msg.edit_text(f"📤 Sending video ({file_size_mb}MB)...")
        print(f"📤 Sending video ({file_size_mb}MB) to user...")

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
        print(f"✅ Video sent successfully to {user.first_name}!")

        # Cleanup
        os.remove(file_path)
        print(f"🧹 Cleaned up: {file_path}")
        print(f"{'='*50}\n")

    except Exception as e:
        await progress_msg.edit_text(f"❌ Failed to download video.\n\n`{str(e)}`")
        print(f"❌ Error: {str(e)}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
            print(f"🧹 Cleaned up failed download: {file_path}")
        print(f"{'='*50}\n")

if __name__ == "__main__":
    request = HTTPXRequest(
        read_timeout=300,
        write_timeout=300,
        connect_timeout=300,
        pool_timeout=300,
    )
    app = ApplicationBuilder().token(TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("🤖 Bot is running... Waiting for messages.")
    app.run_polling()
