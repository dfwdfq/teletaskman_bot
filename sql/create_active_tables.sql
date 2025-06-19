CREATE TABLE IF NOT EXISTS active_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL,
    creator_name TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);
