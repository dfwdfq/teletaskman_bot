import os
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

# Define conversation states
DESCRIPTION = 1
TASK_SELECTION = 2
DONE_TASKS = 3

class Bot:
    def __init__(self):
        load_dotenv()
        self.key = os.getenv("BOT_KEY")
        if not self.key:
            raise Exception("No 'BOT_KEY' in env variables!")
        
        # Create application instance
        self.app = Application.builder().token(self.key).build()
        
        # Create conversation handlers
        add_task_handler = ConversationHandler(
            entry_points=[
                CommandHandler('add', self.start_add_task),
                MessageHandler(filters.Regex(r'^Add$'), self.start_add_task)
            ],
            states={
                DESCRIPTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.save_task)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel_operation)]
        )
        
        complete_task_handler = ConversationHandler(
            entry_points=[
                CommandHandler('done', self.start_done_process),
                MessageHandler(filters.Regex(r'^Done$'), self.start_done_process)
            ],
            states={
                TASK_SELECTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.complete_task)
                ],
            },
            fallbacks=[CommandHandler('cancel', self.cancel_operation)]
        )
        
        # Register handlers
        self.app.add_handler(add_task_handler)
        self.app.add_handler(complete_task_handler)
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("list", self.list_tasks))
        self.app.add_handler(CommandHandler("done_tasks", self.list_done_tasks))
        self.app.add_handler(MessageHandler(filters.Regex(r"^(Add|List|Done Tasks|Done)$"), self.handle_button_click))

    def run(self):
        print("bot is running...")
        self.app.run_polling(poll_interval=5)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        welcome_text = (
            f"Hi {user.mention_html()}! \n\n"
            "I'm a simple script to manage tasks. Here's what you can do:\n"
            "- Add tasks with /add or the Add button\n"
            "- List active tasks with /list or the List button\n"
            "- Complete tasks with /done or the Done button\n"
            "- View completed tasks with /done_tasks or the Done Tasks button"
        )
        await update.message.reply_html(
            welcome_text,
            reply_markup=self.main_menu_keyboard()
        )
        
    async def handle_button_click(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles button clicks from the custom keyboard"""
        button_text = update.message.text
        
        if button_text == "List":
            await self.list_tasks(update, context)
        elif button_text == "Done Tasks":
            await self.list_done_tasks(update, context)
    
    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all active tasks with creator information"""
        tasks = context.user_data.get('tasks', [])
        
        if not tasks:
            await update.message.reply_text(
                "📭 You have no active tasks!",
                reply_markup=self.main_menu_keyboard()
            )
            return
            
        # Format tasks with creator info
        task_list = []
        for idx, task in enumerate(tasks):
            creator_name = task.get('creator_name', 'Unknown')
            creator_id = task.get('creator_id', '')
            
            # Use mention if possible, otherwise fallback to name
            if creator_id:
                creator_display = f"<a href='tg://user?id={creator_id}'>{creator_name}</a>"
            else:
                creator_display = creator_name
                
            task_list.append(
                f"{idx+1}. 🟢 {task['description']} (by {creator_display})"
            )
        
        response = (
            f"📋 *Active Tasks* ({len(tasks)} total):\n\n" +
            "\n".join(task_list) +
            "\n\n_Use /done to complete a task_"
        )
        
        await update.message.reply_html(
            response,
            reply_markup=self.main_menu_keyboard()
        )
    
    async def list_done_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all completed tasks with completion info"""
        done_tasks = context.user_data.get('done_tasks', [])
        
        if not done_tasks:
            await update.message.reply_text(
                "🏆 You haven't completed any tasks yet!",
                reply_markup=self.main_menu_keyboard()
            )
            return
            
        # Format completed tasks with completion info
        task_list = []
        for idx, task in enumerate(done_tasks):
            creator_name = task.get('creator_name', 'Unknown')
            completer_name = task.get('completer_name', 'Unknown')
            completed_at = task.get('completed_at', '')
            
            # Format completion date if available
            if completed_at:
                try:
                    dt = datetime.fromisoformat(completed_at)
                    date_str = dt.strftime("%b %d, %H:%M")
                except:
                    date_str = completed_at
            else:
                date_str = "recently"
                
            task_list.append(
                f"{idx+1}. ✅ {task['description']} "
                f"(by {creator_name}, completed by {completer_name} on {date_str})"
            )
        
        response = (
            f"🏆 *Completed Tasks* ({len(done_tasks)} total):\n\n" +
            "\n".join(task_list)
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
        """Saves the task with creator information"""
        task_description = update.message.text
        user = update.effective_user
        
        # Create task object with creator info
        task = {
            'description': task_description,
            'creator_id': user.id,
            'creator_name': user.full_name,
            'created_at': update.message.date.isoformat()
        }
        
        # Store the task
        context.user_data.setdefault('tasks', []).append(task)
        
        await update.message.reply_text(
            f"✅ Task saved: {task_description}",
            reply_markup=self.main_menu_keyboard()
        )
        return ConversationHandler.END
    
    async def start_done_process(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the task completion process"""
        tasks = context.user_data.get('tasks', [])
        if not tasks:
            await update.message.reply_text(
                "📭 You have no active tasks to complete!",
                reply_markup=self.main_menu_keyboard()
            )
            return ConversationHandler.END
            
        # Format task list with numbers
        task_list = []
        for idx, task in enumerate(tasks):
            task_list.append(f"{idx+1}. {task['description']}")
            
        await update.message.reply_text(
            f"✅ Select a task to mark as done:\n\n" +
            "\n".join(task_list) +
            "\n\nReply with the task number:",
            reply_markup=ReplyKeyboardMarkup([["Cancel"]], resize_keyboard=True)
        )
        return TASK_SELECTION

    async def complete_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Mark a task as completed and move to done tasks"""
        try:
            task_num = int(update.message.text)
            tasks = context.user_data.get('tasks', [])
            
            if 1 <= task_num <= len(tasks):
                # Remove task from active list
                completed_task = tasks.pop(task_num-1)
                
                # Add completion info
                completer = update.effective_user
                completed_task['completer_id'] = completer.id
                completed_task['completer_name'] = completer.full_name
                completed_task['completed_at'] = update.message.date.isoformat()
                
                # Add to done tasks
                context.user_data.setdefault('done_tasks', []).append(completed_task)
                
                # Create completion message
                creator = completed_task.get('creator_name', 'Unknown')
                completer_name = completer.full_name
                
                message = (
                    f"🎉 Task completed!\n"
                    f"• Task: {completed_task['description']}\n"
                    f"• Created by: {creator}\n"
                    f"• Completed by: {completer_name}"
                )
                
                await update.message.reply_text(
                    message,
                    reply_markup=self.main_menu_keyboard()
                )
                return ConversationHandler.END
            else:
                await update.message.reply_text(
                    "⚠️ Invalid task number! Please select from the list.",
                    reply_markup=ReplyKeyboardMarkup([["Cancel"]], resize_keyboard=True)
                )
                return TASK_SELECTION
        except ValueError:
            await update.message.reply_text(
                "❌ Please enter a valid number!",
                reply_markup=ReplyKeyboardMarkup([["Cancel"]], resize_keyboard=True)
            )
            return TASK_SELECTION
    
    async def cancel_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels any ongoing operation"""
        await update.message.reply_text(
            "❌ Operation canceled",
            reply_markup=self.main_menu_keyboard()
        )
        return ConversationHandler.END
    
    @staticmethod
    def main_menu_keyboard():
        return ReplyKeyboardMarkup(
            [["Add", "List", "Done", "Done Tasks"]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
