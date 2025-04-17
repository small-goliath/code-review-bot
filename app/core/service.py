import httpx
import requests
from typing import Any, Callable, Dict
from abc import ABC, abstractmethod
from app.logger import get_logger

class CodeReviewTool(ABC):
    log = get_logger("code-review-tool")

    def __init__(self, base_url: str, username: str, password: str,
                 connect_timeout: float, read_timeout: float,
                 project_id: str, review_id: str, revisions: list[str]):
        
        self.base_url = base_url
        self.username = username
        self.password = password
        self.project_id = project_id
        self.review_id = review_id
        self.revisions = revisions
        self.timeout = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=10.0,
            pool=10.0
        )
    
    @abstractmethod
    async def get_review_details(self, review: Dict[str, Any]):
        pass

    @abstractmethod
    async def get_file_changes(self):
        pass

    @abstractmethod
    async def get_code(file: dict):
        pass

    @abstractmethod
    async def add_comment_to_upsource(self, comment: str):
        pass

class Webhook(ABC):
    log = get_logger("notification")

    def __init__(self, uri: str, body: dict):
        self.body = body
        self.uri = uri

    async def send_message_to_google_chat(self, review_details: dict, code_review_url: str, get_message: Callable[[dict, Dict[str, Any], str], str]):
        self.log.info("웹훅 알림 발송 중...")
        message = await get_message(review_details, self.body, code_review_url)
        text = message.get("text", "")
        attachment = message.get("attachments", [{}])[0]
        fields = attachment.get("fields", [])
        
        field_texts = []
        for field in fields:
            title = field.get("title", "")
            field_value = field.get("value", "")
            field_texts.append(f"{title}: {field_value}")

        if field_texts:
            text += "\n" + "\n".join(field_texts)
        message = {
            "text": text,
            "thread": {
                "threadKey": self.body["data"]["base"]["reviewId"]
            }
        }
        headers = {
            "Content-Type": "application/json"
        }

        self.log.debug(f"webhook message: {message}")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.uri,
                json=message,
                headers=headers
            )
            response.raise_for_status()

    async def get_message_by_created_review(review_details: dict, review: Dict[str, Any], code_review_url: str) -> Dict[str, Any]:
        reviewers = ', '.join(user['userName'] for user in review.get('data', {}).get('base', {}).get('userIds', []))

        try:
            title = review_details['result']['title']

            return {
                "text": f"*{review['data']['base']['actor']['userName']}*님이 리뷰를 생성하였습니다: *{title}* ({review['data']['base']['reviewId']})",
                "attachments": [
                    {
                        "fallback": f"*{review['data']['base']['actor']['userName']}*님이 리뷰를 생성하였습니다: *{title}* ({review['data']['base']['reviewId']})",
                        "fields": [
                            {
                                "title": "Project",
                                "value": review['projectId'],
                                "short": True
                            },
                            {
                                "title": "Participant(s)",
                                "value": reviewers,
                                "short": True
                            },
                            {
                                "title": "link",
                                "value": f"<{code_review_url}/{review['projectId']}/review/{review['data']['base']['reviewId']}>"
                            }
                        ],
                        "color": "#F35A00"
                    }
                ]
            }
        except requests.RequestException as e:
            raise Exception(f"Error fetching review details: {e}")