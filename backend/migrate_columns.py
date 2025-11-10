#backend/migrate_columns.py
# backend/migrate_columns.py
import asyncio
from sqlalchemy import text
from app.config.database import engine

async def migrate():
    async with engine.begin() as conn:
        migrations = [
            "ALTER TABLE projects ALTER COLUMN name TYPE VARCHAR(200);",
            "ALTER TABLE projects ALTER COLUMN domain TYPE VARCHAR(200);",
            "ALTER TABLE projects ALTER COLUMN duration TYPE VARCHAR(300);",
        ]
        
        for sql in migrations:
            try:
                print(f"Running: {sql}")
                await conn.execute(text(sql))
                print("✅ Success\n")
            except Exception as e:
                print(f"❌ Error: {e}\n")
    
    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate())