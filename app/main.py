from fastapi import FastAPI, Response, Request
from fastapi.routing import APIRoute
from starlette.background import BackgroundTask
from starlette.types import Message

from app.api.main import api_router
from app.config import settings
from app.logger import get_logger

log = get_logger('review-bot')

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(api_router)

async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {'type': 'http.request', 'body': body}
    request._receive = receive

def log_http(req_body, res_body):
    log.debug(f"request body: {req_body.decode('utf-8')}")
    log.debug(f"response body: {res_body.decode('utf-8')}")

@app.middleware('http')
async def some_middleware(request: Request, call_next):
    req_body = await request.body()
    await set_body(request, req_body)
    response = await call_next(request)
    
    res_body = b''
    async for chunk in response.body_iterator:
        res_body += chunk
    
    task = BackgroundTask(log_http, req_body, res_body)
    return Response(content=res_body, status_code=response.status_code, 
        headers=dict(response.headers), media_type=response.media_type, background=task)