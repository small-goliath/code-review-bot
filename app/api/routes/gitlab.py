
import asyncio
from pathlib import Path
import traceback
from fastapi import APIRouter, Request
from app.core import adapter
from app.core.gpt import GPT
from app.core.model import EventType, WebhookMessage
from app.logger import get_logger
from app.config import settings

router = APIRouter()

log = get_logger('review-bot')

@router.get("/gitlab")
async def upsource_webhook(request: Request):
    try:
        event = await request.json()
        gitlab = adapter.get_code_review_tool(code_review_tool=settings.CODE_REVIEW_TOOL,
                                              base_url=settings.GITLAB_BASE_URL,
                                              private_token=settings.GITLAB_ACCESS_TOKEN,
                                              event=event)
        
        message_format = await WebhookMessage.from_gitlab(event)
        webhook = adapter.get_notification(webhook=settings.WEBHOOK,
                                           uri=settings.WEBHOOK_URI,
                                           message_format=message_format)
        asyncio.create_task(webhook.send_message())

        if message_format.event_type != EventType.CREATED_REVIEW:
            return {"status": "success"}

        changes = await gitlab.get_file_changes()

        review_comments = []

        for file in changes['changes']:
            file_path = file['new_path']
            ext = Path(file_path).suffix.lstrip(".")

            if ext not in settings.REVIEW_FILES:
                log.warning(f"{ext} 확장자는 리뷰 대상이 아닙니다.")
                continue
            diff = file['diff']

            # openai 코드 리뷰 요청
            gpt = GPT()
            comment = await gpt.generate_code_review_by_diff(
                file_name=file_path, diff=diff
            )
            if comment:
                review_comments.append(comment)

        # 코드 리뷰 내용 작성
        if review_comments:
            await gitlab.add_comment(review_comments)
        else:
            log.warning("생성된 리뷰 코멘트가 없습니다.")

        return {"status": "success"}
    except Exception as e:
        log.error(f"오류 발생: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}