from fastapi import FastAPI
from client_bot import client_routes

app = FastAPI(title="AutoDB API")

app.include_router(client_routes.router, prefix="/clients", tags=["Клиенты"])
