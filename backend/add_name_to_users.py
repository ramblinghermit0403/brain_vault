import sqlite3
import os

# Path to the database
DB_PATH = "backend/brain_vault.db"

def run_migration():
    print(f"Checking database at {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("Database not found! Please ensure backend/brain_vault.db exists.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Migrating 'users' table...")
        cursor.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "name" not in columns:
            print("Adding column 'name'...")
            cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
            print("Column 'name' added successfully.")
        else:
            print("Column 'name' already exists.")

        conn.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
