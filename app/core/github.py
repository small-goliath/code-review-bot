from github import Github as PyGithub
from github.PullRequest import PullRequest
from typing import Any, Dict
from app.core.service import CodeReviewTool

class Github(CodeReviewTool):
    def __init__(self, base_url: str,
                 private_token: str,
                 repo_name: str,
                 pull_number: int):
        super().__init__(base_url)
        self.private_token = private_token
        self.repo_name = repo_name
        self.pull_number = pull_number

        self.gh = PyGithub(self.private_token, base_url=base_url)
        self.repo = self.gh.get_repo(self.repo_name)
        self.pr: PullRequest = self.repo.get_pull(self.pull_number)

    async def get_review_details(self) -> Dict[str, Any]:
        # 예: PR 제목, 작성자, 본문 등
        return {
            "title": self.pr.title,
            "body": self.pr.body,
            "user": self.pr.user.login,
            "state": self.pr.state,
        }

    async def get_file_changes(self) -> Dict[str, Any]:
        # 변경된 파일 목록과 diff 정보
        files = self.pr.get_files()
        return {
            file.filename: {
                "status": file.status,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "patch": file.patch,
            }
            for file in files
        }

    async def get_code(self, file_path: str, ref: str) -> str:
        # 특정 ref (SHA, 브랜치명 등)의 파일 내용 가져오기
        file_content = self.repo.get_contents(file_path, ref=ref)
        return file_content.decoded_content.decode()

    async def add_comment(self, comments: list[str]) -> None:
        # PR 전체에 대한 일반 코멘트
        comment = "\n\n".join(comments)
        self.pr.create_issue_comment(comment)
