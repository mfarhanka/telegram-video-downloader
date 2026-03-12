import os
import uuid
import yt_dlp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Send me an Instagram video link, and I will download it for you.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    if "instagram.com" not in url:
        await update.message.reply_text("Please send a valid Instagram link.")
        return

    message = await update.message.reply_text("Downloading video... Please wait.")
    
    # Generate a unique filename
    filename = f"{uuid.uuid4()}.mp4"
    
    ydl_opts = {
        'outtmpl': filename,
        'format': 'b[ext=mp4]/b',  # Use 'b' (best combined format) to avoid needing FFmpeg
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=open(filename, 'rb'),
            reply_to_message_id=update.message.message_id,
            read_timeout=120,
            write_timeout=120,
            connect_timeout=120,
            pool_timeout=120
        )
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message.message_id)
        
    except Exception as e:
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message.message_id, text=f"Failed to download video: {str(e)}")
    
    finally:
        # Cleanup the downloaded file
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
