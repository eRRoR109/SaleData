CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT(20) NOT NULL,
    email TEXT NOT NULL,
    u_type TEXT(5) NOT NULL,
    password TEXT
);
