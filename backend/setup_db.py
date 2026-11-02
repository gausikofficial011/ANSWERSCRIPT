import asyncio
import asyncpg


async def setup():
    conn = await asyncpg.connect("postgresql://postgres:postgres@localhost:5432/postgres")
    dbs = await conn.fetch("SELECT datname FROM pg_database WHERE datname = 'answer_evaluation'")
    if not dbs:
        await conn.execute("CREATE DATABASE answer_evaluation")
        print("Database created: answer_evaluation")
    else:
        print("Database already exists: answer_evaluation")
    await conn.close()


asyncio.run(setup())
