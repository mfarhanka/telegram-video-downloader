# Telegram Instagram Video Downloader Bot

A simple Telegram bot that downloads Instagram videos when a user sends an Instagram link.

## Prerequisites

- [Python 3.8+](https://www.python.org/downloads/) installed on your machine.
- A Telegram account to create a bot.

## Installation Instructions

### 1. Create a Telegram Bot
1. Open Telegram and search for **@BotFather**.
2. Send the `/newbot` command and follow the text prompts to name your bot.
3. Once completed, BotFather will give you a **Bot API Token** (e.g., `123456789:ABCdefGHIJklmNOPQrsTUVwxyZ`). Copy this token.

### 2. Set Up the Project
1. Clone or download this project to your machine.
2. Open your terminal (or PowerShell/Command Prompt) and navigate to the project directory:
   ```bash
   cd path/to/telegram-video-downloader
   ```

### 3. Create a Virtual Environment (Recommended)
Creating a virtual environment keeps the required libraries separate from your main system.

**For Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
Run the following command to install the necessary Python packages (`python-telegram-bot`, `yt-dlp`, and `python-dotenv`):
```bash
pip install -r requirements.txt
```
*(If you don't have a requirements.txt yet, you can run: `pip install python-telegram-bot yt-dlp python-dotenv`)*

### 5. Configure Environment Variables
1. Make a copy of the `.env.example` file and rename it to `.env`:
   **Windows:** `copy .env.example .env`
   **macOS/Linux:** `cp .env.example .env`
2. Open the `.env` file in your text editor and paste your bot token:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_from_botfather_here
   ```

### 6. Run the Bot
Start the bot by running the main Python file:
```bash
python bot.py
```

Your bot is now running! Open Telegram, search for your bot, click "Start", and send it an Instagram video link to test it out.
