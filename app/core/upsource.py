import httpx
from typing import Any, Dict
from app.core.service import CodeReviewTool

class Upsource(CodeReviewTool):
    def __init__(self, base_url: str,
                 username: str,
                 password: str,
                 connect_timeout: float,
                 read_timeout: float,
                 project_id: str,
                 review_id: str,
                 revisions: list[str]):
        super().__init__(base_url, username, password, connect_timeout, read_timeout)
        self.project_id = project_id
        self.review_id = review_id
        self.revisions = revisions

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path}"

    async def _post(self, path: str, payload: dict) -> dict:
        url = self._build_url(path)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                auth=(self.username, self.password),
                json=payload,
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                self.log.error(f"HTTP 오류 발생: {e.response.status_code} - {e.response.text}")
                raise
            return response.json()

    async def get_review_details(self) -> dict:
        self.log.info("Upsource 리뷰 상세 정보를 조회합니다.")
        payload = {
            "projectId": self.project_id,
            "reviewId": self.review_id,
        }
        return await self._post("~rpc/getReviewDetails", payload)

    async def get_file_changes(self) -> dict:
        self.log.info("리뷰의 변경 파일 목록을 조회합니다.")
        payload = {
            "reviewId": {
                "projectId": self.project_id,
                "reviewId": self.review_id,
            },
            "revisions": {
                "revisions": self.revisions,
                "selectAll": True,
            },
        }
        return await self._post("~rpc/getReviewSummaryChanges", payload)

    async def get_code(self, file: Dict[str, str]) -> dict:
        self.log.info(f"파일 '{file['fileName']}'의 코드 내용을 조회합니다.")
        payload = {
            "projectId": file["projectId"],
            "revisionId": file["revisionId"],
            "fileName": file["fileName"],
        }
        return await self._post("~rpc/getFileContent", payload)

    async def add_comment(self, comments: list[str]) -> None:
        self.log.info("AI 리뷰 코멘트를 Upsource에 등록합니다.")
        payload = {
            "anchor": {},
            "reviewId": {
                "projectId": self.project_id,
                "reviewId": self.review_id,
            },
            "text": "\n\n".join(comments),
            "projectId": self.project_id,
            "labels": {"name": "ai-review"},
        }
        await self._post("~rpc/createDiscussion", payload)
