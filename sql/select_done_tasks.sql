SELECT 
    id, 
    creator_id, 
    creator_name, 
    description, 
    created_at,
    completer_id,
    completer_name,
    completed_at
FROM done_tasks
ORDER BY completed_at DESC;