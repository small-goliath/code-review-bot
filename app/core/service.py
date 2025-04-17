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

    def __init__(self, uri: str, body: dict, code_review_url: str):
        self.body = body
        self.uri = uri
        self.code_review_url = code_review_url

    async def send_message(self, review_details: dict = None):
        self.log.info("웹훅 알림 발송 중...")
        message = self._get_message(self.body, review_details)
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

    def _get_review_info(self, review: Dict[str, Any]) -> Dict[str, str]:
        base = review.get('data', {}).get('base', {})
        return {
            'review_id': base.get('reviewId', ''),
            'project_id': review.get('projectId', ''),
            'actor': base.get('actor', {}).get('userName', 'unknown'),
            'reviewers': ', '.join(user.get('userName', '') for user in base.get('userIds', [])),
            'url': f"{self.code_review_url}/{review.get('projectId', '')}/review/{base.get('reviewId', '')}",
        }

    def _build_attachment(self, fields: list[dict], fallback: str, color: str) -> Dict[str, Any]:
        return {
            "attachments": [
                {
                    "fallback": fallback,
                    "fields": fields,
                    "color": color
                }
            ]
        }

    def _get_message_by_created_review(self, review_details: dict, review: Dict[str, Any]) -> Dict[str, Any]:
        info = self._get_review_info(review)
        title = review_details['result']['title']
        text = f"*{info['actor']}*님이 리뷰를 생성하였습니다: *{title}* ({info['review_id']})"

        fields = [
            {"title": "Project", "value": info['project_id'], "short": True},
            {"title": "Participant(s)", "value": info['reviewers'], "short": True},
            {"title": "link", "value": f"<{info['url']}>"}
        ]

        return {"text": text, **self._build_attachment(fields, text, "#F35A00")}


    def _get_message_by_changed_review_state(self, review_details: dict, review: Dict[str, Any]) -> Dict[str, Any]:
        info = self._get_review_info(review)
        title = review_details['result']['title']
        old_state, new_state = review['data']['oldState'], review['data']['newState']
        state_map = {0: '_Open_', 1: '_Closed_'}
        text = f"리뷰 상태가 {state_map[old_state]}에서 {state_map[new_state]}로 변경되었습니다: *{title}* ({info['review_id']})"

        fields = [
            {"title": "Project", "value": info['project_id'], "short": True},
            {"title": "Changed by", "value": info['actor'], "short": True},
            {"title": "link", "value": f"<{info['url']}>"}
        ]

        color = "#F35A00" if new_state == 0 else "#2AB27B"
        return {"text": text, **self._build_attachment(fields, text, color)}


    def _get_message_by_changed_participant_state(self, review_details: dict, review: Dict[str, Any]) -> Dict[str, Any]:
        info = self._get_review_info(review)
        title = review_details['result']['title']
        participant = review['data']['participant'].get('userName') or review['data']['participant'].get('userId', 'unknown')
        old_state, new_state = review['data']['oldState'], review['data']['newState']
        state_map = {0: '_Unread_', 1: '_Read_', 2: '_Accepted_', 3: '_Rejected_'}
        text = f"{participant}님이 {state_map[old_state]}에서 {state_map[new_state]}로 변경하였습니다: *{title}* ({info['review_id']})"

        fields = [
            {"title": "Project", "value": info['project_id'], "short": True},
            {"title": "Participant(s)", "value": info['reviewers'], "short": True},
            {"title": "link", "value": f"<{info['url']}>"}
        ]

        color = "#F35A00" if new_state == 3 else "#2AB27B"
        return {"text": text, **self._build_attachment(fields, text, color)}


    def _get_message_by_created_discussion(self, review: Dict[str, Any]) -> Dict[str, Any]:
        info = self._get_review_info(review)
        comment = review['data'].get('commentText', '')
        url = f"{self.code_review_url}/{info['project_id']}"
        if info['review_id']:
            url += f"/review/{info['review_id']}"

        text = f"*{info['actor']}*님이 댓글을 작성했습니다: *{info['project_id']}*"
        fields = [
            {"title": "Project", "value": info['project_id'], "short": True},
            {"title": "Participant(s)", "value": info['reviewers'], "short": True},
            {"title": "Comment", "value": comment},
            {"title": "link", "value": f"<{url}>"}
        ]

        return {"text": text, **self._build_attachment(fields, text, "#3AA3E3")}
    

    def _get_message(self, review: Dict[str, Any], review_details: dict = None):
        if review['dataType'] == 'ReviewCreatedFeedEventBean':
            return self._get_message_by_created_review(review_details, review)