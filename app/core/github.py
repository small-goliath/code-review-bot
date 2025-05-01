import json
from github import Github as PyGithub
from github import Auth as PyGithubAuth
from github.PullRequest import PullRequest
from typing import Any, Dict, List, Optional
from app.core.service import CodeReviewTool

class Github(CodeReviewTool):
    def __init__(self,
                 private_token: str,
                 repo_name: str,
                 actor: str,
                 action: str,
                 pr_number: Optional[str] = None,
                 organization_name: Optional[str] = None):
        super().__init__()
        self.private_token = private_token
        self.repo_name = repo_name
        self.actor = actor
        self.action = action
        self.github = PyGithub(auth=PyGithubAuth.Token(private_token))
        self.pr_number = pr_number
        self.organization_name = organization_name

    async def get_review_details(self) -> List[Dict[str, Any]]:
        if self.organization_name is None:
            return []
        
        org = self.github.get_organization(self.organization_name)
        members = org.get_members()
        return [
            {
                "member_name": member.name,
                "member_email": member.email
            }
            for member in members
        ]

    async def get_file_changes(self) -> List[Dict[str, Any]]:
        repo = self.github.get_repo(self.repo_name)
        pr: PullRequest = repo.get_pull(self.pr_number)
        files = pr.get_files()

        return [
            {
                "patch": file.patch,
                "file_name": file.filename
            }
            for file in files
        ]

    async def add_comment(self, comments: list[str]):
        comment = "\n\n".join(comments)
        repo = self.github.get_repo(self.repo_name)
        pr: PullRequest = repo.get_pull(self.pr_number)
        pr.create_issue_comment(comment)

    async def add_review_comment(self, comments: list[str]):
        repo = self.github.get_repo(self.repo_name)
        pr: PullRequest = repo.get_pull(self.pr_number)

        for comment in comments:
            comment = comment.removeprefix("```json").removesuffix("```")
            comment_detail = json.loads(comment)
            if isinstance(comment_detail, list):
                for detail in comment_detail:
                    pr.create_review_comment(body=detail['body'],
                                        path=detail['path'],
                                        line=detail['start_line'],
                                        commit=pr.get_commits().reversed[0])
            else:
                pr.create_review_comment(body=comment_detail['body'],
                                    path=comment_detail['path'],
                                    line=comment_detail['start_line'],
                                    commit=pr.get_commits().reversed[0])
