from discord_webhook.webhook import DiscordWebhook
import slack_webhook
import httpx
from app.core.service import Webhook

class GoogleChat(Webhook):
    async def send_message(self):
        self.log.info(f"google chat 알림 발송 중...{self.uri}")
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

class Slack(Webhook):
    async def send_message(self):
        self.log.info(f"slack 알림 발송 중...{self.uri}")
        message = self._get_message(self.message_format)
        slack = slack_webhook.Slack(url=self.uri)
        slack.post(text=message['text'], attachments=message['attachments'])

class Discord(Webhook):
    async def send_message(self):
        self.log.info(f"discord 알림 발송 중...{self.uri}")
        message = self._get_message(self.message_format)
        text = message.get("text", "")
        attachment = message.get("attachments", [{}])[0]
        fields = attachment.get("fields", [])
        embeds = [
            {
                "fields": [{"name": field.get("title", ""), "value": field.get("value", ""), "inline": True} for field in fields],
                "color": 1127128
            }
        ]

        discord = DiscordWebhook(url=self.uri, content=text, embeds=embeds)

        message = {
            "content": text,
            "embeds": [
                {
                    "fields": [{"name": field.get("title", ""), "value": field.get("value", ""), "inline": True} for field in fields],
                    "color": 1127128
                }
            ]
        }

        discord.execute()