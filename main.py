from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from asyncpg import Pool, create_pool, Record
import asyncio

app = FastAPI()

db_pool: Pool = None

class Post(BaseModel):
    id: int
    title: str
    content: str

DATABASE_URL = "postgresql://user:password@localhost:5432/blog"  # CHANGE AS NEEDED

@app.on_event("startup")
async def startup():
    global db_pool
    db_pool = await create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    global db_pool
    if db_pool:
        await db_pool.close()

@app.get("/posts", response_model=List[Post])
async def get_posts():
    try:
        async with db_pool.acquire() as connection:
            records: List[Record] = await connection.fetch("SELECT id, title, content FROM posts ORDER BY id ASC")
            posts = [Post(**dict(record)) for record in records]
            return posts
    except Exception as e:
        # Log the error here in production
        raise HTTPException(status_code=500, detail="Failed to fetch posts.")
