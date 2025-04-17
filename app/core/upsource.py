import httpx
import requests
from typing import Any, Dict
from app.core.service import CodeReviewTool

class Upsource(CodeReviewTool):
    async def get_review_details(self, review: Dict[str, Any]):
        response = requests.post(
            f"{self.base_url}/~rpc/getReviewDetails",
            auth=(self.username, self.password),
            json={
                "projectId": review['projectId'],
                "reviewId": review['data']['base']['reviewId']
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_file_changes(self):
        self.log.info("변경된 파일 리스트 업...")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/~rpc/getReviewSummaryChanges",
                auth=(self.username, self.password),
                json={"reviewId": {"projectId": self.project_id, "reviewId": self.review_id}, "revisions": {"revisions": self.revisions, "selectAll": True}}
            )
            response.raise_for_status()
            return response.json()

    async def get_code(self, file: dict):
        self.log.info("파일 코드 가져오는 중...")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/~rpc/getFileContent",
                auth=(self.username, self.password),
                json={"projectId": file['projectId'], "revisionId": file['revisionId'], "fileName": file['fileName']}
            )
            response.raise_for_status()
            return response.json()

    async def add_comment_to_upsource(self, comment: str):
        self.log.info("업소스에 리뷰 작성 중...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/~rpc/createDiscussion",
                auth=(self.username, self.password),
                json={"anchor": {}, "reviewId": {"projectId": self.project_id, "reviewId": self.review_id}, "text": comment, "projectId": self.project_id, "labels": {"name": "ai-review"}}
            )
            response.raise_for_status()