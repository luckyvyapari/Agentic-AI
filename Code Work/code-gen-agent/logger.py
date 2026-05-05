import sqlite3
import os
import json
from datetime import datetime

DB_NAME = "agent_history.db"

def init_db():
    """Initializes the SQLite database for logging agent activities."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            thread_id TEXT,
            node_name TEXT,
            iteration INTEGER,
            status TEXT,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_event(thread_id, node_name, iteration, status, data=None):
    """Logs an event to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_json = json.dumps(data) if data else None
    
    cursor.execute('''
        INSERT INTO logs (timestamp, thread_id, node_name, iteration, status, data)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, thread_id, node_name, iteration, status, data_json))
    
    conn.commit()
    conn.close()

def get_logs(thread_id=None):
    """Retrieves logs from the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if thread_id:
        cursor.execute("SELECT * FROM logs WHERE thread_id = ? ORDER BY id DESC", (thread_id,))
    else:
        cursor.execute("SELECT * FROM logs ORDER BY id DESC")
        
    rows = cursor.fetchall()
    conn.close()
    return rows
