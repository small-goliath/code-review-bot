
import asyncio
import traceback
from pathlib import Path
from fastapi import APIRouter, Request
from app.core.gpt.gpt import GPT
from app.core.service import CodeReviewTool, Webhook
from app.core.upsource import Upsource
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
        revisions = event["data"]["revisions"]

        if settings.CODE_REVIEW_TOOL == "upsource":
            code_review_tool = Upsource(base_url=settings.CODE_REVIEW_BASE_URL, username=settings.CODE_REVIEW_TOOL_ACCOUNT_USERNAME, password=settings.CODE_REVIEW_TOOL_ACCOUNT_PASSWORD, connect_timeout=10.0, read_timeout=10.0, project_id=project_id, review_id=review_id, revisions=revisions)

        webhook = Webhook(uri=settings.WEBHOOK_URI, body=event)
        review_details = await code_review_tool.get_review_details(event)
        asyncio.create_task(webhook.send_message_to_google_chat(review_details=review_details, code_review_url=code_review_tool.base_url, get_message=Webhook.get_message_by_created_review))



        if event.get("dataType") != "ReviewCreatedFeedEventBean":
            return {"status": "success"}

        files = await code_review_tool.get_file_changes()
        review_comments = []

        for file in files['result']['diff']['diff']:
            # 각 변경된 파일에 대한 코드 가져오기
            if 'oldFile' in file:
                old_file_name, old_code = await process_file(file['oldFile'], code_review_tool)
            new_file_name, new_code = await process_file(file['newFile'], code_review_tool)

            if not new_file_name:
                continue

            # openai 코드 리뷰 요청
            gpt = GPT()
            comment = await gpt.generate_code_review(
                old_file_name, old_code, new_file_name, new_code
            )
            if comment:
                review_comments.append(comment)

        # upsource 코드 리뷰 내용 작성
        if review_comments:
            await code_review_tool.add_comment_to_upsource(review_comments)
        else:
            log.warning("생성된 리뷰 코멘트가 없습니다.")

        return {"status": "success"}

    except Exception as e:
        log.error(f"웹훅 처리 중 오류 발생: {e}")
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