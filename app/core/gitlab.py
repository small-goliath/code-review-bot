import gitlab
from typing import Any, Dict
from app.core.service import CodeReviewTool

class Gitlab(CodeReviewTool):
    def __init__(self, base_url: str,
                 private_token: str,
                 project_path: str):
        super().__init__(base_url)
        self.private_token = private_token
        self.gl = gitlab.Gitlab(url=self.base_url, private_token=self.private_token)
        self.project_path = project_path

    def get_review_details(event: dict) -> Dict[str, Any]:
        return {
            ""
        }

    def get_file_changes(self) -> Dict[str, Any]:
        """Merge Request에서 변경된 파일 목록"""
        return self.mr.changes()

    def get_code(self, file_path: str, ref: str) -> str:
        """지정된 브랜치(ref)의 파일 내용"""
        f = self.project.files.get(file_path=file_path, ref=ref)
        return f.decode().decode('utf-8')

    def add_comment(self, comment: str) -> None:
        """Merge Request에 코멘트 추가"""
        self.mr.notes.create({'body': f"[AI Review]\n{comment}"})