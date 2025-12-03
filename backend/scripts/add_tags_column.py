import sqlite3
import os

DB_PATH = "backend/brain_vault.db"

def add_tags_column():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(memories)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "tags" in columns:
            print("'tags' column already exists in 'memories' table.")
        else:
            print("Adding 'tags' column to 'memories' table...")
            cursor.execute("ALTER TABLE memories ADD COLUMN tags JSON")
            conn.commit()
            print("Column added successfully.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_tags_column()
