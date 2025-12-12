import sqlite3
import os

# Path to the database
DB_PATH = "backend/brain_vault.db"

def run_migrations():
    print(f"Checking database at {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("Database not found! Run backend server/init_db.py first to create base schema.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Update memories table
        print("Migrating 'memories' table...")
        # Check if columns exist to avoid errors on re-run
        cursor.execute("PRAGMA table_info(memories)")
        columns = [info[1] for info in cursor.fetchall()]
        
        new_cols = {
            "source_llm": "TEXT DEFAULT 'user'",
            "model_name": "TEXT",
            "importance_score": "REAL DEFAULT 0.0",
            "status": "TEXT DEFAULT 'approved'",
            "task_type": "TEXT",
            "version": "INTEGER DEFAULT 1"
        }
        
        for col, dtype in new_cols.items():
            if col not in columns:
                print(f"Adding column {col}...")
                cursor.execute(f"ALTER TABLE memories ADD COLUMN {col} {dtype}")
            else:
                print(f"Column {col} already exists.")

                print(f"Column {col} already exists.")

        # 1.5 Update users table
        print("Migrating 'users' table...")
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "settings" not in columns:
            print("Adding column settings...")
            cursor.execute("ALTER TABLE users ADD COLUMN settings JSON DEFAULT '{}'")
        else:
            print("Column settings already exists.")

        # 1.6 Add 'show_in_inbox' column to memories
        print("Checking 'show_in_inbox' column...")
        cursor.execute("PRAGMA table_info(memories)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "show_in_inbox" not in columns:
            print("Adding 'show_in_inbox' column to memories...")
            cursor.execute("ALTER TABLE memories ADD COLUMN show_in_inbox BOOLEAN DEFAULT 1")
            
            # Update existing non-pending memories to NOT show in inbox
            print("Cleaning up inbox status for existing items...")
            cursor.execute("UPDATE memories SET show_in_inbox = 0 WHERE status != 'pending'")
        else:
            print("Column 'show_in_inbox' already exists.")

        # 2. Create ai_clients table
        print("Creating 'ai_clients' table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            encrypted_api_key TEXT NOT NULL,
            permissions JSON,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_used_at DATETIME,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_ai_clients_id ON ai_clients (id)")

        # 3. Create memory_history table
        print("Creating 'memory_history' table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_id INTEGER NOT NULL,
            old_content TEXT,
            new_content TEXT,
            actor TEXT NOT NULL,
            actor_type TEXT DEFAULT 'user',
            change_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(memory_id) REFERENCES memories(id)
        )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_memory_history_id ON memory_history (id)")

        # 4. Create audit_logs table
        print("Creating 'audit_logs' table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            target_id TEXT,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_audit_logs_id ON audit_logs (id)")
        
        # 5. Create memory_clusters table
        print("Creating 'memory_clusters' table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_clusters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            memory_ids JSON NOT NULL,
            representative_text TEXT,
            avg_similarity REAL DEFAULT 0.0,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_memory_clusters_id ON memory_clusters (id)")

        conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_migrations()
