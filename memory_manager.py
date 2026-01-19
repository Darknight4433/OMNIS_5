import sqlite3
import time
import os

class MemoryManager:
    def __init__(self, db_path="omnis_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize tables for history and facts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversation history: (timestamp, user_id, user_msg, ai_msg)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                user_id TEXT,
                user_message TEXT,
                ai_message TEXT
            )
        ''')
        
        # User facts: (user_id, key, value)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_facts (
                user_id TEXT,
                fact_key TEXT,
                fact_value TEXT,
                last_updated REAL,
                PRIMARY KEY (user_id, fact_key)
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_conversation(self, user_id, user_msg, ai_msg):
        """Add a round of conversation to history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversation_history (timestamp, user_id, user_message, ai_message) VALUES (?, ?, ?, ?)",
            (time.time(), user_id, user_msg, ai_msg)
        )
        conn.commit()
        conn.close()

    def get_recent_history(self, user_id, limit=5):
        """Get the last N exchanges for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_message, ai_message FROM conversation_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        # Return in chronological order
        return rows[::-1]

    def store_fact(self, user_id, key, value):
        """Store or update a fact about a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user_facts (user_id, fact_key, fact_value, last_updated) VALUES (?, ?, ?, ?)",
            (user_id, key, value, time.time())
        )
        conn.commit()
        conn.close()

    def get_user_facts(self, user_id):
        """Retrieve all known facts for a user as a formatted string or dict."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT fact_key, fact_value FROM user_facts WHERE user_id = ?",
            (user_id,)
        )
        facts = cursor.fetchall()
        conn.close()
        return {k: v for k, v in facts}

    def get_latest_topic(self, user_id):
        """Fetch the latest significant topic or user query for follow-up."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_message FROM conversation_history 
            WHERE user_id = ? 
            AND length(user_message) > 15
            ORDER BY timestamp DESC LIMIT 1
        ''', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

if __name__ == "__main__":
    # Self-test
    mem = MemoryManager("test_memory.db")
    mem.add_conversation("User123", "Hello", "Hi there!")
    print("History:", mem.get_recent_history("User123"))
    mem.store_fact("User123", "hobby", "coding")
    print("Facts:", mem.get_user_facts("User123"))
    os.remove("test_memory.db")
