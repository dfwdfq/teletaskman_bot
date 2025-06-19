import os
import sqlite3 as sql
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from dotenv import load_dotenv
from datetime import datetime

from database import Database

# Define conversation states
DESCRIPTION = 1
TASK_SELECTION = 2

class Bot:
    def __init__(self):
        load_dotenv()
        self.key = os.getenv("BOT_KEY")
        if not self.key:
            raise Exception("No 'BOT_KEY' in env variables!")
        
        # Initialize database
        self.db = Database()
        
        # Create application instance
        self.app = Application.builder().token(self.key).build()
        
        # Create conversation handlers with improved cancel handling
        add_task_handler = ConversationHandler(
            entry_points=[
                CommandHandler('add', self.start_add_task),
                MessageHandler(filters.Regex(r'^Add$'), self.start_add_task)
            ],
            states={
                DESCRIPTION: [
                    MessageHandler(filters.TEXT & ~filters.Regex(r'^Cancel$'), self.save_task)
                ],
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel_operation),
                MessageHandler(filters.Regex(r'^Cancel$'), self.cancel_operation)
            ]
        )
        
        complete_task_handler = ConversationHandler(
            entry_points=[
                CommandHandler('done', self.start_done_process),
                MessageHandler(filters.Regex(r'^Done$'), self.start_done_process)
            ],
            states={
                TASK_SELECTION: [
                    MessageHandler(filters.TEXT & ~filters.Regex(r'^Cancel$'), self.complete_task)
                ],
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel_operation),
                MessageHandler(filters.Regex(r'^Cancel$'), self.cancel_operation)
            ]
        )
        
        # Register handlers
        self.app.add_handler(add_task_handler)
        self.app.add_handler(complete_task_handler)
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("list", self.list_tasks))
        self.app.add_handler(CommandHandler("done_tasks", self.list_done_tasks))
        self.app.add_handler(MessageHandler(filters.Regex(r"^(List|Done Tasks|Done)$"), self.handle_button_click))

        # Add error handler
        self.app.add_error_handler(self.error_handler)

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log errors and send a message to the user"""
        print(f"Update {update} caused error {context.error}")
        if update and hasattr(update, 'message'):
            await update.message.reply_text(
                "⚠️ An error occurred. Please try again later.",
                reply_markup=self.main_menu_keyboard()
            )

    def run(self):
        print("Bot is running...")
        self.app.run_polling(poll_interval=5)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        welcome_text = (
            f"Hi {user.mention_html()}! \n\n"
            "I'm a simple script to manage tasks. Here's what you can do:\n"
            "- Add tasks with /add or the Add button\n"
            "- List active tasks with /list or the List button\n"
            "- Complete tasks with /done or the Done button\n"
            "- View completed tasks with /done_tasks or the Done Tasks button\n\n"
            "You can cancel any action by pressing the Cancel button"
        )
        await update.message.reply_html(
            welcome_text,
            reply_markup=self.main_menu_keyboard()
        )
        
    async def handle_button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        button_text = update.message.text
        
        if button_text == "List":
            await self.list_tasks(update, context)
        elif button_text == "Done Tasks":
            await self.list_done_tasks(update, context)
        
    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tasks = self.db.get_active_tasks()
        
        if not tasks:
            await update.message.reply_text(
                "📭 You have no active tasks!",
                reply_markup=self.main_menu_keyboard()
            )
            return
            
        task_list = []
        for task in tasks:
            task_id, creator_id, creator_name, description, created_at = task
            
            # Format creation date
            try:
                dt = datetime.fromisoformat(created_at)
                date_str = dt.strftime("%b %d, %H:%M")
            except:
                date_str = created_at
                
            task_list.append(
                f"{task_id}. 🟢 {description} "
                f"(by {creator_name} on {date_str})"
            )
        
        response = (
            f"📋 *Active Tasks* ({len(tasks)} total):\n\n" +
            "\n".join(task_list) +
            "\n\n_Use /done [ID] to complete a task_"
        )
        
        await update.message.reply_markdown(
            response,
            reply_markup=self.main_menu_keyboard()
        )
    
    async def list_done_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tasks = self.db.get_done_tasks()
        
        if not tasks:
            await update.message.reply_text(
                "🏆 You haven't completed any tasks yet!",
                reply_markup=self.main_menu_keyboard()
            )
            return
            
        task_list = []
        for task in tasks:
            (task_id, creator_id, creator_name, description, created_at, 
             completer_id, completer_name, completed_at) = task
            
            # Format dates
            try:
                created_dt = datetime.fromisoformat(created_at)
                created_str = created_dt.strftime("%b %d")
                completed_dt = datetime.fromisoformat(completed_at)
                completed_str = completed_dt.strftime("%b %d, %H:%M")
            except:
                created_str = created_at
                completed_str = completed_at
                
            task_list.append(
                f"✅ {description} (ID: {task_id})\n"
                f"   - Created by: {creator_name} on {created_str}\n"
                f"   - Completed by: {completer_name} on {completed_str}"
            )
        
        response = (
            f"🏆 *Completed Tasks* ({len(tasks)} total):\n\n" +
            "\n\n".join(task_list)
        )
        
        await update.message.reply_text(
            response,
            reply_markup=self.main_menu_keyboard()
        )

    async def start_add_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Starts the task creation process"""
        await update.message.reply_text(
            "📝 Please describe your task:",
            reply_markup=ReplyKeyboardMarkup([["Cancel"]], resize_keyboard=True)
        )
        return DESCRIPTION

    async def save_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Saves the task description and ends the conversation"""
        # Check if user pressed Cancel
        if update.message.text.lower() == "cancel":
            return await self.cancel_operation(update, context)
            
        description = update.message.text
        user = update.effective_user
        created_at = datetime.now().isoformat()
        
        # Save to database
        task_id = self.db.add_task(
            user.id, 
            user.full_name, 
            description, 
            created_at
        )
        
        await update.message.reply_text(
            f"✅ Task #{task_id} saved: {description}",
            reply_markup=self.main_menu_keyboard()
        )
        return ConversationHandler.END
    
    async def start_done_process(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the task completion process"""
        tasks = self.db.get_active_tasks()
        if not tasks:
            await update.message.reply_text(
                "📭 You have no active tasks to complete!",
                reply_markup=self.main_menu_keyboard()
            )
            return ConversationHandler.END
            
        await update.message.reply_text(
            "✅ Reply with the ID of the task you want to complete\n"
            "Or press Cancel to abort",
            reply_markup=ReplyKeyboardMarkup([["Cancel"]], resize_keyboard=True)
        )
        return TASK_SELECTION

    async def complete_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Mark a task as completed based on user selection"""
        # Check if user pressed Cancel
        if update.message.text.lower() == "cancel":
            return await self.cancel_operation(update, context)
            
        try:
            task_id = int(update.message.text)
            user = update.effective_user
            completed_at = datetime.now().isoformat()
            
            # Complete task in database
            success = self.db.complete_task(
                task_id,
                user.id,
                user.full_name,
                completed_at
            )
            
            if success:
                task = self.db.get_task(task_id)
                if task:
                    _, creator_id, creator_name, description, _ = task
                    message = (
                        f"🎉 Task #{task_id} completed!\n"
                        f"• Task: {description}\n"
                        f"• Created by: {creator_name}\n"
                        f"• Completed by: {user.full_name}"
                    )
                else:
                    message = f"✅ Task #{task_id} marked as completed"
                
                await update.message.reply_text(
                    message,
                    reply_markup=self.main_menu_keyboard()
                )
                return ConversationHandler.END
            else:
                await update.message.reply_text(
                    "⚠️ Invalid task ID! Please enter a valid task number.",
                    reply_markup=ReplyKeyboardMarkup([["Cancel"]], resize_keyboard=True)
                )
                return TASK_SELECTION
        except ValueError:
            await update.message.reply_text(
                "❌ Please enter a valid task number!",
                reply_markup=ReplyKeyboardMarkup([["Cancel"]], resize_keyboard=True)
            )
            return TASK_SELECTION
    
    async def cancel_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels any ongoing operation and returns to main menu"""
        await update.message.reply_text(
            "❌ Operation canceled",
            reply_markup=self.main_menu_keyboard()
        )
        return ConversationHandler.END
    
    @staticmethod
    def main_menu_keyboard():
        """Main menu keyboard without Help button"""
        return ReplyKeyboardMarkup(
            [[ "Add", "List", "Done", "Done Tasks"]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
