# Private Task Manager Bot for Couples

![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)

A private Telegram bot designed exclusively for couples to manage tasks together. This bot helps partners stay organized while maintaining privacy and intimacy in their shared activities.

**GitHub Repository**: [dfwdfq/teletaskman](https://github.com/dfwdfq/teletaskman)

## Features ✨

- **Exclusive access** - Only you and your partner can use the bot
- **Shared task management** - Create, track, and complete tasks together
- **Personal attribution** - See who created and completed each task
- **Activity history** - Review completed tasks with timestamps
- **Intuitive interface** - Simple buttons and commands
- **Persistent storage** - SQLite database remembers all your tasks
- **Task reindexing** - Automatic numbering of active tasks
- **Cancel anytime** - Stop operations with one click

## Setup Guide ⚙️

### 1. Prerequisites
- Python 3.8+
- Telegram account
- Bot token from [@BotFather](https://t.me/BotFather)

### 2. Installation
```bash
git clone https://github.com/dfwdfq/teletaskman.git
cd teletaskman
python -m venv venv

# Activate virtual environment:
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. Configuration
```bash
cp .env.example .env
```
Edit `.env` with your details:
```env
BOT_KEY=your_telegram_bot_token_here
ALLOWED_USERS=your_user_id,partners_user_id
```

### 4. Run the Bot
```bash
python bot.py
```

## How to Use 🤖

### Main Menu
```
[ Add ] [ List ] [ Done ] [ Done Tasks ]
```

### Basic Workflow
1. **Add a task**  
   Click `Add` → Describe task ("Buy groceries")  
   *Bot saves task with your name*

2. **Complete a task**  
   Click `Done` → Select task number (1)  
   *Bot marks it complete with partner's name*

3. **Review history**  
   Click `Done Tasks`  
   *Shows completed tasks with creator/completer info*

### All Commands
- `/start` - Begin using the bot
- `/add` - Create a new task
- `/list` - Show active tasks
- `/done` - Complete a task
- `/done_tasks` - View completed tasks
- `/cancel` - Stop current operation

## Security & Privacy 🔒

- Strict user whitelisting (only pre-approved IDs work)
- All data stored locally in SQLite database
- No third-party services or cloud storage
- Private task history visible only to you two

## Customization 🎨

Personalize these elements for your relationship:
```python
# In bot.py - Customize welcome message
welcome_text = (
    f"Hi {user.mention_html()}! \n\n"
    "Our private task manager is ready! ❤️\n"
    "- Add tasks with /add or Add button\n"
    ...
)

# Customize keyboard buttons
return ReplyKeyboardMarkup(
    [["💌 Add", "📋 List", "✅ Done", "🏆 History"]],
    ...
)
```

## Support ❤️

For help with setup or customization:
[Open an Issue](https://github.com/dfwdfq/teletaskman/issues)

---

**Designed with love for couples who want to stay organized together** 💑  
*Because sharing tasks is another way of sharing your life*