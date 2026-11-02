PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS categories (
id INTEGER PRIMARY KEY CHECK (id > 0),
name TEXT NOT NULL UNIQUE
CHECK (length(trim(name)) BETWEEN 2 AND 40)
);
CREATE TABLE IF NOT EXISTS records (
id INTEGER PRIMARY KEY CHECK (id > 0),
code TEXT NOT NULL UNIQUE
CHECK (length(trim(code)) BETWEEN 3 AND 40),
title TEXT NOT NULL
CHECK (length(trim(title)) BETWEEN 3 AND 120),
category_id INTEGER NOT NULL
CHECK (typeof(category_id) = 'integer' AND category_id > 0),
value INTEGER NOT NULL
CHECK (typeof(value) = 'integer' AND value >= 0),
status TEXT NOT NULL
CHECK (status IN ('new', 'in_progress', 'done')),
FOREIGN KEY (category_id) REFERENCES categories(id)
ON DELETE RESTRICT
);
COMMIT;