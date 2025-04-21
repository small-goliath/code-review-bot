
import asyncio
import traceback
from pathlib import Path
from fastapi import APIRouter, Request
from app.core import adapter
from app.core.gpt import GPT
from app.core.model import EventType, WebhookMessage
from app.core.service import CodeReviewTool
from app.logger import get_logger
from app.config import settings

router = APIRouter()

log = get_logger('review-bot')

@router.get("/upsource")
async def upsource_webhook(request: Request):
    try:
        event = await request.json()
        review_id = event["data"]["base"]["reviewId"]
        project_id = event["projectId"]
        revisions = event["data"].get("revisions", "")

        upsource = adapter.get_code_review_tool(code_review_tool=settings.CODE_REVIEW_TOOL,
                                                base_url=settings.UPSOURCE_BASE_URL,
                                                username=settings.UPSOURCE_USERNAME,
                                                password=settings.UPSOURCE_PASSWORD,
                                                project_id=project_id,
                                                review_id=review_id,
                                                revisions=revisions)

        review_details = await upsource.get_review_details()
        message_format = await WebhookMessage.from_upsource(event, review_details['result']['title'])
        webhook = adapter.get_notification(webhook=settings.WEBHOOK,
                                           uri=settings.WEBHOOK_URI,
                                           message_format=message_format,
                                           code_review_url=upsource.base_url)
        asyncio.create_task(webhook.send_message())

        if message_format.event_type != EventType.CREATED_REVIEW:
            return {"status": "success"}

        files = await upsource.get_file_changes()
        review_comments = []

        for file in files['result']['diff']['diff']:
            # 각 변경된 파일에 대한 코드 가져오기
            if 'oldFile' in file:
                old_file_name, old_code = await process_file(file['oldFile'], upsource)
            new_file_name, new_code = await process_file(file['newFile'], upsource)

            if not new_file_name:
                continue

            # openai 코드 리뷰 요청
            gpt = GPT()
            comment = await gpt.generate_code_review_by_files(
                old_file_name, old_code, new_file_name, new_code
            )
            if comment:
                review_comments.append(comment)

        # upsource 코드 리뷰 내용 작성
        if review_comments:
            await upsource.add_comment(review_comments)
        else:
            log.warning("생성된 리뷰 코멘트가 없습니다.")

        return {"status": "success"}

    except Exception as e:
        log.error(f"오류 발생: {e}")
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


async def process_file(file_info: dict, code_review_tool: CodeReviewTool) -> tuple[str | None, str | None]:
    if not file_info:
        return None, None

    file_name = str(file_info.get("fileName", ""))
    ext = Path(file_name).suffix.lstrip(".")

    if ext not in settings.REVIEW_FILES:
        log.warning(f"{ext} 확장자는 리뷰 대상이 아닙니다.")
        return None, None

    code = await code_review_tool.get_code(file_info)
    return file_name, code