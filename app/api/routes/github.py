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

@router.post("/github")
async def upsource_webhook(request: Request):
    try:
        event = await request.json()
        github = adapter.get_code_review_tool(code_review_tool=settings.CODE_REVIEW_TOOL,
                                              private_token=settings.GITHUB_ACCESS_TOKEN,
                                              event=event)

        review_details = await github.get_review_details()
        message_format = await WebhookMessage.from_github(event, review_details)
        webhook = adapter.get_notification(webhook=settings.WEBHOOK,
                                           uri=settings.WEBHOOK_URI,
                                           message_format=message_format)

        asyncio.create_task(webhook.send_message())

        if message_format.event_type != EventType.CREATED_REVIEW:
            return {"status": "success"}
        
        # 각 변경된 파일에 대한 코드 가져오기
        changes = await github.get_file_changes()
        
        review_comments = []

        for file in changes:
            ext = Path(file['file_name']).suffix.lstrip(".")

            if ext not in settings.REVIEW_FILES:
                log.warning(f"{ext} 확장자는 리뷰 대상이 아닙니다.")
                continue

            # openai 코드 리뷰 요청
            gpt = GPT()
            comment = await gpt.generate_structor_output_code_review_by_diff(
                file_name=file['file_name'], diff=file['patch']
            )
            if comment:
                review_comments.append(comment)

        if review_comments:
            await github.add_review_comment(review_comments)
        else:
            log.warning("생성된 리뷰 코멘트가 없습니다.")

    except Exception as e:
        log.error(f"오류 발생: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}