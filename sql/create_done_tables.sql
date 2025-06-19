CREATE TABLE IF NOT EXISTS done_tasks (
    id INTEGER PRIMARY KEY,
    creator_id INTEGER NOT NULL,
    creator_name TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL,
    completer_id INTEGER NOT NULL,
    completer_name TEXT NOT NULL,
    completed_at TEXT NOT NULL
);
