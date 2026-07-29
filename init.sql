CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed only if table is empty (idempotent)
INSERT INTO tasks (title, done)
SELECT 'Buy milk', FALSE
WHERE NOT EXISTS (SELECT 1 FROM tasks);

INSERT INTO tasks (title, done)
SELECT 'Write report', FALSE
WHERE NOT EXISTS (SELECT 1 FROM tasks);

INSERT INTO tasks (title, done)
SELECT 'Walk the dog', TRUE
WHERE NOT EXISTS (SELECT 1 FROM tasks);