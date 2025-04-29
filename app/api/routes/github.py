
import asyncio
import traceback
from fastapi import APIRouter, Request
from app.core import adapter
from app.core.gpt import GPT
from app.core.model import EventType, WebhookMessage
from app.logger import get_logger
from app.config import settings

router = APIRouter()

log = get_logger('review-bot')

@router.get("/github")
async def upsource_webhook(request: Request):
    try:
        event = await request.json()
        log.info(f"recv webhook: {event}")
        github = adapter.get_code_review_tool(code_review_tool=settings.CODE_REVIEW_TOOL,
                                              base_url=settings.GITHUB_BASE_URL,
                                              private_token=settings.GITHUB_ACCESS_TOKEN)
        
        message_format = await WebhookMessage.from_gitlab(event)
        webhook = adapter.get_notification(webhook=settings.WEBHOOK,
                                           uri=settings.WEBHOOK_URI,
                                           message_format=message_format,
                                           code_review_url=github.base_url)
        asyncio.create_task(webhook.send_message())

        if message_format.event_type != EventType.CREATED_REVIEW:
            return {"status": "success"}

    except Exception as e:
        log.error(f"오류 발생: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
