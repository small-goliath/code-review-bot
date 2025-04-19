import gitlab
from typing import Any, Dict
from app.core.service import CodeReviewTool

class Gitlab(CodeReviewTool):
    def __init__(self, base_url: str,
                 private_token: str,
                 project_id: str,
                 merge_request_iid: int):
        super().__init__(base_url)
        self.private_token = private_token
        self.gl = gitlab.Gitlab(url=self.base_url, private_token=self.private_token)
        self.project_id = project_id
        self.merge_request_iid = merge_request_iid
        self.project = self.gl.projects.get(self.project_id)
        self.mr = self.project.mergerequests.get(self.merge_request_iid)

    async def get_review_details(self) -> Dict[str, Any]:
        pass

    async def get_file_changes(self) -> Dict[str, Any]:
        return self.mr.changes()

    async def get_code(self, file_path: str, ref: str) -> str:
        pass

    async def add_comment(self, comments: list[str]) -> None:
        comment = "\n\n".join(comments)
        self.mr.notes.create({'body': comment})