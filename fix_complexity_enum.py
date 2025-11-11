#fix_complexity_enum.py
# fix_complexity_enum.py
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def fix_complexity():
    """Fix complexity enum values in database"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        try:
            print("🔄 Updating complexity values from 'medium' to 'moderate'...")
            
            # Update all 'medium' values to 'moderate'
            await conn.execute(text("""
                UPDATE projects 
                SET complexity = 'moderate' 
                WHERE complexity = 'medium'
            """))
            
            print("✅ Successfully updated complexity values!")
            
            # Show updated records
            result = await conn.execute(text("SELECT id, name, complexity FROM projects"))
            projects = result.fetchall()
            
            print(f"\n📊 Current projects:")
            for project in projects:
                print(f"   - {project[1]}: {project[2]}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            raise
    
    await engine.dispose()
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    asyncio.run(fix_complexity())