import httpx
from app.core.service import Webhook

class GoogleChat(Webhook):
    async def send_message(self):
        self.log.info("google chat 알림 발송 중...")
        message = self._get_message(self.message_format)
        text = message.get("text", "")
        attachment = message.get("attachments", [{}])[0]
        fields = attachment.get("fields", [])
        
        field_texts = []
        for field in fields:
            field_texts.append(f"{field.get("title", "")}: {field.get("value", "")}")

        if field_texts:
            text += "\n" + "\n".join(field_texts)
        message = {
            "text": text,
            "thread": {
                "threadKey": str(self.message_format.review_id)
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.uri,
                json=message,
                headers=headers
            )
            response.raise_for_status()

# TODO: used slack_sdk lib
class Slack(Webhook):
    async def send_message(self):
        self.log.info("slack 알림 발송 중...")
        message = self._get_message(self.message_format)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.uri,
                json=message
            )
            response.raise_for_status()

# TODO: used discord lib
class Discord(Webhook):
    async def send_message(self):
        self.log.info("discord 알림 발송 중...")
        message = self._get_message(self.message_format)
        text = message.get("text", "")
        attachment = message.get("attachments", [{}])[0]
        fields = attachment.get("fields", [])

        message = {
            "content": text,
            "embeds": [
                {
                    "fields": [{"name": field.get("title", ""), "value": field.get("value", ""), "inline": True} for field in fields],
                    "color": 1127128
                }
            ]
        }

        if len(message) > 2000:
            message = message[:1997] + "..."

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.uri,
                json=message
            )
            response.raise_for_status()