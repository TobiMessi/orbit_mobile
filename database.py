import sqlite3

DB_PATH = "orbit.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            ip TEXT NOT NULL,
            port INTEGER DEFAULT 5001,
            is_active INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def get_user_servers(user_id):
    return query_db("SELECT * FROM servers WHERE user_id = ?", (user_id,))

def add_server(user_id, name, ip, port=5001):
    query_db("INSERT INTO servers (user_id, name, ip, port) VALUES (?, ?, ?, ?)", (user_id, name, ip, port))

def set_active_server(user_id, server_id):
    query_db("UPDATE servers SET is_active = 0 WHERE user_id = ?", (user_id,))
    query_db("UPDATE servers SET is_active = 1 WHERE id = ? AND user_id = ?", (server_id, user_id))

def get_active_server(user_id):
    return query_db("SELECT * FROM servers WHERE user_id = ? AND is_active = 1", (user_id,), one=True)

def delete_server(server_id, user_id):
    query_db("DELETE FROM servers WHERE id = ? AND user_id = ?", (server_id, user_id))
