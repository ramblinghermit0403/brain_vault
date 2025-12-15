import asyncio
import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import engine
from sqlalchemy import text

async def migrate_db():
    print("Starting Advanced RAG Database Migration...")
    async with engine.begin() as conn:
        
        # 1. Update chunks table
        print("Altering 'chunks' table...")
        # Check if columns exist to avoid errors (idempotency-ish)
        # SQLite vs Postgres syntax differs slightly, assuming Postgres based on conversation history "Migrating the relational database... to PostgreSQL"
        # Using "IF NOT EXISTS" logic via exception handling or generic add
        
        columns_to_add = [
            "ADD COLUMN IF NOT EXISTS summary TEXT",
            "ADD COLUMN IF NOT EXISTS generated_qas JSONB",
            "ADD COLUMN IF NOT EXISTS tokens_count INTEGER",
            "ADD COLUMN IF NOT EXISTS trust_score FLOAT DEFAULT 0.5",
            "ADD COLUMN IF NOT EXISTS last_validated_at TIMESTAMP",
            "ADD COLUMN IF NOT EXISTS feedback_score FLOAT DEFAULT 0.0",
            "ADD COLUMN IF NOT EXISTS entities JSONB",
            "ADD COLUMN IF NOT EXISTS tags JSONB"
        ]
        
        for col_sql in columns_to_add:
            try:
                await conn.execute(text(f"ALTER TABLE chunks {col_sql};"))
                print(f"Executed: {col_sql}")
            except Exception as e:
                print(f"Skipped/Error (might already exist): {col_sql} -> {e}")

        # 2. Create feedback_events table
        print("Creating 'feedback_events' table...")
        create_feedback_sql = """
        CREATE TABLE IF NOT EXISTS feedback_events (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            chunk_id INTEGER NOT NULL REFERENCES chunks(id),
            document_id INTEGER REFERENCES documents(id),
            event_type VARCHAR(50) NOT NULL,
            context JSONB,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        await conn.execute(text(create_feedback_sql))
        print("Created/Verified 'feedback_events' table.")

    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_db())
