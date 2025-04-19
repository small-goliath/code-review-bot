from typing import Optional
from app.core.gitlab import Gitlab
from app.core.model import WebhookMessage
from app.core.notification import Discord, GoogleChat, Slack
from app.core.service import CodeReviewTool, Webhook
from app.core.upsource import Upsource

def get_notification(webhook: str, uri: str, message_format: WebhookMessage, code_review_url: str) -> Webhook:
        if webhook == 'google-chat':
            return GoogleChat(uri=uri,
                              message_format=message_format,
                              code_review_url=code_review_url)
        elif webhook == 'slack':
            return Slack(uri=uri,
                         message_format=message_format,
                         code_review_url=code_review_url)
        elif webhook == 'discord':
            return Discord(uri=uri,
                           message_format=message_format,
                           code_review_url=code_review_url)
        else:
            raise Exception(f"{webhook}는 지원되지 않습니다.")
        
def get_code_review_tool(code_review_tool: str,
                         base_url: str,
                         username: Optional[str] = None,
                         password: Optional[str] = None,
                         project_id: Optional[str] = None,
                         review_id: Optional[str] = None,
                         revisions: Optional[str] = None,
                         private_token: Optional[str] = None,
                         mr_iid: Optional[int] = None,
                         ) -> CodeReviewTool:
        if code_review_tool == 'upsource':
            return Upsource(base_url=base_url,
                            username=username,
                            password=password,
                            connect_timeout=10.0,
                            read_timeout=10.0,
                            project_id=project_id,
                            review_id=review_id,
                            revisions=revisions)
        elif code_review_tool == 'gitlab':
            return Gitlab(base_url=base_url,
                          private_token=private_token,
                          project_id=project_id,
                          merge_request_iid=mr_iid)
        else:
            raise Exception(f"{code_review_tool}는 지원되지 않습니다.")
     