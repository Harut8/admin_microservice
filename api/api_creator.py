from fastapi import FastAPI, Request
from api.admin_api import admin_router
from uvicorn import run
from repository.core.core import DbConnection
from service.redis_client.redis_client import RedisClient

app = FastAPI(version="1.0.0")
app.include_router(admin_router, prefix="/api/v1")


@app.on_event("startup")
async def on_start_server():
    await DbConnection.create_connection()
    RedisClient()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    x = request.query_params
    # print(await request.body())
    response = await call_next(request)
    return response


@app.get("/")
def ping():
    return {"status": "SERVER RUNNING"}


def run_server():
    run(app, port=8004)
