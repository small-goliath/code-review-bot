import httpx
from typing import Any, Dict
from abc import ABC, abstractmethod
from app.core.model import EventType, WebhookMessage
from app.logger import get_logger

class CodeReviewTool(ABC):
    log = get_logger("code-review-tool")

    def __init__(self, base_url: str,
                 username: str = None,
                 password: str = None,
                 connect_timeout: float = 10.0,
                 read_timeout: float = 10.0):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.timeout = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=10.0,
            pool=10.0
        )
    
    @abstractmethod
    async def get_review_details(self):
        pass

    @abstractmethod
    async def get_file_changes(self):
        pass

    @abstractmethod
    async def get_code(file: dict):
        pass

    @abstractmethod
    async def add_comment(self, comments: list[str]):
        pass

class Webhook(ABC):
    log = get_logger("notification")

    def __init__(self,
                 uri: str,
                 message_format: WebhookMessage,
                 code_review_url: str):
        self.message_format = message_format
        self.uri = uri
        self.code_review_url = code_review_url

    @abstractmethod
    async def send_message(self):
        pass

    def _get_review_info(self) -> Dict[str, str]:
        return {
            'review_id': self.message_format.review_id,
            'project_id': self.message_format.project_name,
            'actor': self.message_format.actor_name,
            'reviewers': self.message_format.reviewers,
            'url': f"{self.code_review_url}/{self.message_format.project_name}/review/{self.message_format.review_id}",
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

    def _get_message_by_created_review(self, title: str) -> Dict[str, Any]:
        info = self._get_review_info()
        text = f"*{info['actor']}*님이 리뷰를 생성하였습니다: *{title}* ({info['review_id']})"

        fields = [
            {"title": "Project", "value": info['project_id'], "short": True},
            {"title": "Participant(s)", "value": info['reviewers'], "short": True},
            {"title": "link", "value": f"<{info['url']}>"}
        ]

        return {"text": text, **self._build_attachment(fields, text, "#F35A00")}


    def _get_message_by_changed_review_state(self, title: str) -> Dict[str, Any]:
        info = self._get_review_info()
        old_state, new_state = self.message_format.old_state, self.message_format.new_state
        state_map = {0: '`Open`', 1: '`Closed`'}

        if state_map[old_state]:
            text = f"리뷰 상태가 {state_map[old_state]}에서 {state_map[new_state]}로 변경되었습니다: *{title}* ({info['review_id']})"
        else:
            text = f"리뷰 상태가 {state_map[new_state]}로 변경되었습니다: *{title}* ({info['review_id']})"

        fields = [
            {"title": "Project", "value": info['project_id'], "short": True},
            {"title": "Changed by", "value": info['actor'], "short": True},
            {"title": "link", "value": f"<{info['url']}>"}
        ]

        color = "#F35A00" if new_state == 0 else "#2AB27B"
        return {"text": text, **self._build_attachment(fields, text, color)}


    def _get_message_by_changed_participant_state(self, title: str) -> Dict[str, Any]:
        info = self._get_review_info()
        # participant = review['data']['participant'].get('userName') or review['data']['participant'].get('userId', 'unknown')
        old_state, new_state = self.message_format.old_state, self.message_format.new_state
        state_map = {0: '`Unread`', 1: '`Read`', 2: '`Accepted`', 3: '`Rejected`'}
        if state_map[old_state]:
            text = f"리뷰 상태가 {state_map[old_state]}에서 {state_map[new_state]}로 변경되었습니다: *{title}* ({info['review_id']})"
        else:
            text = f"리뷰 상태가 {state_map[new_state]}로 변경되었습니다: *{title}* ({info['review_id']})"

        fields = [
            {"title": "Project", "value": info['project_id'], "short": True},
            {"title": "Participant(s)", "value": info['reviewers'], "short": True},
            {"title": "link", "value": f"<{info['url']}>"}
        ]

        color = "#F35A00" if new_state == 3 else "#2AB27B"
        return {"text": text, **self._build_attachment(fields, text, color)}


    def _get_message_by_created_discussion(self) -> Dict[str, Any]:
        info = self._get_review_info()
        url = f"{self.code_review_url}/{info['project_id']}"
        if info['review_id']:
            url += f"/review/{info['review_id']}"

        text = f"*{info['actor']}*님이 댓글을 작성했습니다: *{info['project_id']}*"
        fields = [
            {"title": "Project", "value": info['project_id'], "short": True},
            {"title": "Participant(s)", "value": info['reviewers'], "short": True},
            {"title": "Comment", "value": self.message_format.comment},
            {"title": "link", "value": f"<{url}>"}
        ]

        return {"text": text, **self._build_attachment(fields, text, "#3AA3E3")}
    

    def _get_message(self, message_format: WebhookMessage) -> dict:
        if self.message_format.event_type == EventType.CREATED_REVIEW:
            return self._get_message_by_created_review(message_format.title)
        elif self.message_format.event_type == EventType.CHANGED_REVIEW_STATE:
            return self._get_message_by_changed_review_state(message_format.title)
        elif self.message_format.event_type == EventType.CHANGED_REVIEWER_STATE:
            return self._get_message_by_changed_participant_state(message_format.title)
        elif self.message_format.event_type == EventType.CREATED_COMMENT:
            return self._get_message_by_created_discussion()
        else:
            raise Exception(f'{self.message_format.event_type}은 지원되지 않습니다.')