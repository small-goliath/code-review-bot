from typing import Optional
from app.core.gitlab import Gitlab
from app.core.github import Github
from app.core.model import WebhookMessage
from app.core.notification import Discord, GoogleChat, Slack
from app.core.service import CodeReviewTool, Webhook
from app.core.upsource import Upsource

def get_notification(webhook: str, uri: str, message_format: WebhookMessage) -> Webhook:
        if webhook == 'google-chat':
            return GoogleChat(uri=uri,
                              message_format=message_format)
        elif webhook == 'slack':
            return Slack(uri=uri,
                         message_format=message_format)
        elif webhook == 'discord':
            return Discord(uri=uri,
                           message_format=message_format)
        else:
            raise Exception(f"{webhook}는 지원되지 않습니다.")

     
def get_code_review_tool(code_review_tool: str,
                         event: dict,
                         base_url: Optional[str] = None,
                         private_token: Optional[str] = None,
                         username: Optional[str] = None,
                         password: Optional[str] = None,
                         ) -> CodeReviewTool:
        if code_review_tool == 'upsource':
            return Upsource(base_url=base_url,
                            username=username,
                            password=password,
                            connect_timeout=10.0,
                            read_timeout=10.0,
                            project_id=event["data"]["base"]["reviewId"],
                            review_id=event["projectId"],
                            revisions=event["data"].get("revisions", ""))
        elif code_review_tool == 'gitlab':
            return Gitlab(base_url=base_url,
                          private_token=private_token,
                          project_id=event['project']['id'],
                          merge_request_iid=event['object_attributes']['iid'])
        elif code_review_tool == 'github':
            return Github(private_token=private_token,
                          repo_name=event["repository"]["full_name"],
                          actor=event["sender"]["login"],
                          action=event["action"],
                          pr_number=event.get('pull_request', {}).get('number', None),
                          organization_name=event.get('organization', {}).get('login', None))
        else:
            raise Exception(f"{code_review_tool}는 지원되지 않습니다.")
     