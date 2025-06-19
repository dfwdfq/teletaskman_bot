import sqlite3 as sql
import os

def sqlify(command):
    '''do REALLY dirty work in sql'''
    def wrapper(self, *args, **kwargs):
        connection = sql.connect('data.sql')
        cursor = connection.cursor()
        
        #really funny trick
        result = command(self, cursor, *args, **kwargs)
        
        connection.commit()
        connection.close()
        return result
    return wrapper

class Database:
    def __init__(self):
        self.scripts = {}
        self.sql_path = "teletaskman/sql/"
        self.read_scripts()

        if not os.path.exists("data.sql"):
            print("start database creating...")

        self.create_tables()
            
                     
    def _read_file(self, sql_file: str):
        with open(self.sql_path + sql_file, "r") as f:
            return f.read()
        
    def read_scripts(self):
        t_files = [x for x in os.listdir(self.sql_path) if x.endswith(".sql")]
        for f in t_files:
            key, _ = f.split(".")
            self.scripts[key] = self._read_file(f)

    @sqlify
    def create_tables(self, cursor):
        creators = [x for x in self.scripts.keys() if "create" in x]
        for c in creators:
            cursor.execute(self.scripts[c])
