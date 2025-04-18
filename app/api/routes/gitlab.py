
import asyncio
import traceback
from fastapi import APIRouter, Request
from app.core import adapter
from app.core.gitlab import Gitlab
from app.core.model import WebhookMessage
from app.logger import get_logger
from app.config import settings

router = APIRouter()

log = get_logger('review-bot')

@router.get("/gitlab")
async def upsource_webhook(request: Request):
    try:
        event = await request.json()
        gitlab = Gitlab(base_url=settings.GITLAB_BASE_URL,
            private_token=settings.GITLAB_ACCESS_TOKEN,
            project_path=event['project']['id'])
        
        message_format = await WebhookMessage.from_gitlab(event)
        webhook = adapter.get_notification(webhook=settings.WEBHOOK,
                                           uri=settings.WEBHOOK_URI,
                                           message_format=message_format,
                                           code_review_url=gitlab.base_url)
        asyncio.create_task(webhook.send_message())
    except Exception as e:
        log.error(f"오류 발생: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}