import asyncio
from fastapi import FastAPI
from client_bot.client_routes import router as client_router
from client_bot.client import start_bot as start_client_bot

app = FastAPI()
app.include_router(client_router)

async def main():
    bot_task = asyncio.create_task(start_client_bot())

    await asyncio.gather(bot_task)

if __name__ == "__main__":
    asyncio.run(main())
