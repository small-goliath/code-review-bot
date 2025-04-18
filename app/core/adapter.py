from app.core.model import WebhookMessage
from app.core.notification import Discord, GoogleChat, Slack
from app.core.service import Webhook

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