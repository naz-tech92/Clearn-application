PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL,
    fullname_normalized TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    present_skill_career TEXT NOT NULL,
    school TEXT NOT NULL,
    country TEXT NOT NULL,
    phone_number TEXT NOT NULL UNIQUE,
    firebase_uid TEXT,
    auth_provider TEXT NOT NULL DEFAULT 'password',
    email_verified INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS login_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    email TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    provider TEXT NOT NULL DEFAULT 'password',
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    email TEXT,
    channel TEXT NOT NULL,
    user_message TEXT NOT NULL,
    assistant_reply TEXT,
    source TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS pending_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    fullname TEXT NOT NULL,
    present_skill_career TEXT NOT NULL,
    school TEXT NOT NULL,
    country TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    firebase_uid TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);
