import sqlite3 as sql
import os

class Database:
    def __init__(self):
        self.scripts = {}
        self.sql_path = "teletaskman/sql/" 
        self.read_scripts()

        if not os.path.exists("data.sql"):
            print("Creating new database...")
            self.create_tables()

        self.task_buffer = None
            
    def _read_file(self, sql_file: str):
        with open(os.path.join(self.sql_path, sql_file), "r") as f:
            return f.read()
        
    def read_scripts(self):            
        t_files = [x for x in os.listdir(self.sql_path) if x.endswith(".sql")]
        for f in t_files:
            key, _ = os.path.splitext(f)
            self.scripts[key] = self._read_file(f)


    def sqlify(command):
        """Decorator for SQL operations"""
        def wrapper(self, *args, **kwargs):
            connection = sql.connect('data.sql')
            cursor = connection.cursor()
            
            # Execute the command
            result = command(self, cursor, *args, **kwargs)
            
            connection.commit()
            connection.close()
            return result
        return wrapper

    @sqlify
    def create_tables(self, cursor):
        creators = [x for x in self.scripts.keys() if "create" in x]
        for c in creators:
            cursor.execute(self.scripts[c])
            
    @sqlify
    def add_task(self, cursor, user_id, username, description, created_at):
        cursor.execute(
            self.scripts["insert_active_task"], 
            (user_id, username, description, created_at)
        )
        return cursor.lastrowid
            
    @sqlify
    def get_active_tasks(self, cursor):
        cursor.execute(self.scripts["select_active_tasks"])
        return cursor.fetchall()
    
    @sqlify
    def get_task(self, cursor, task_id):
        cursor.execute(self.scripts["select_task"], (task_id,))
        return cursor.fetchone()

    @sqlify
    def complete_task(self, cursor, task_id, completer_id, completer_name, completed_at):
        # Get task details
        task = self.get_task(task_id)
        if not task:
            return False
    
        # Unpack task tuple
        task_id, creator_id, creator_name, description, created_at = task
    
        # Move to done_tasks
        cursor.execute(
            self.scripts["insert_done_task"],
            (task_id, creator_id, creator_name, description, created_at, 
             completer_id, completer_name, completed_at)
        )
    
        # Remove from active_tasks
        cursor.execute(self.scripts["delete_active_task"], (task_id,))
        return True
    
    @sqlify
    def get_done_tasks(self, cursor):
        cursor.execute(self.scripts["select_done_tasks"])
        return cursor.fetchall()
