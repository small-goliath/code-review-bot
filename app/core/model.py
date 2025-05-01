from enum import Enum, auto
from typing import Any, Dict, List, Optional
from app.config import settings

class EventType(Enum):
    CREATED_REVIEW = auto()
    CHANGED_REVIEW_STATE = auto()
    CHANGED_REVIEWER_STATE = auto()
    CREATED_COMMENT = auto()

    @staticmethod
    def get_type(event_type: str):
        try:
            return EVENT_TYPE_MAPPING[event_type]
        except KeyError:
            raise Exception(f'{event_type}은 지원되지 않습니다.')

EVENT_TYPE_MAPPING = {
    'ReviewCreatedFeedEventBean': EventType.CREATED_REVIEW,
    'merge_request': EventType.CREATED_REVIEW,
    'ReviewStateChangedFeedEventBean': EventType.CHANGED_REVIEW_STATE,
    'ParticipantStateChangedFeedEventBean': EventType.CHANGED_REVIEWER_STATE,
    'DiscussionFeedEventBean': EventType.CREATED_COMMENT,
    'pr': EventType.CREATED_REVIEW,
    'comment': EventType.CREATED_COMMENT,
}

class WebhookMessage():
    def __init__(self,
                 title: str,
                 project_name: str,
                 event_type: EventType,
                 actor_name: str,
                 reviewers: list[str],
                 review_id: str,
                 old_state: Optional[str] = None,
                 new_state: Optional[str] = None,
                 comment: Optional[str] = None,
                 url: Optional[str] = None,
                 ):
        self.title = title
        self.project_name = project_name
        self.event_type = event_type
        self.actor_name = actor_name
        self.reviewers = reviewers
        self.review_id = review_id
        self.old_state = old_state
        self.new_state = new_state
        self.comment = comment
        self.url = url

    async def from_upsource(upsource_event: dict, title: str) -> 'WebhookMessage' :
        return WebhookMessage(title = title,
                              project_name=upsource_event['projectId'],
                              event_type = EventType.get_type(upsource_event['dataType']),
                              actor_name = upsource_event['data']['base']['actor']['userName'],
                              reviewers = ', '.join(user.get('userName', '') for user in upsource_event['data']['base'].get('userIds', [])),
                              review_id = upsource_event['data']['base']['reviewId'],
                              old_state = upsource_event['data'].get('oldState', None),
                              new_state = upsource_event['data'].get('newState', None),
                              comment = upsource_event['data'].get('commentText', None),
                              url = f"{settings.UPSOURCE_BASE_URL}/{upsource_event['projectId']}/review/{upsource_event['data']['base']['reviewId']}")
    
    async def from_gitlab(gitlab_event: dict) -> 'WebhookMessage' :
        # TODO: MR 외 title
        return WebhookMessage(title=f"{gitlab_event['object_attributes']['source_branch']} into {gitlab_event['object_attributes']['target_branch']}",
                              project_name=gitlab_event['project']['name'],
                              event_type = EventType.get_type(gitlab_event['event_type']),
                              # TODO: gitlab_event['user']['username']??
                              actor_name = gitlab_event['user']['name'],
                              # TODO: gitlab_event['reviewers']['username']??
                              reviewers = ', '.join(user.get('name', '') for user in gitlab_event.get('reviewers',[])),
                              review_id = gitlab_event['object_attributes']['iid'],
                              new_state = gitlab_event['object_attributes'].get('action', None),
                              comment = gitlab_event.get('commit', {}).get('message', None),
                              url=gitlab_event.get('object_attributes', {}).get('url', settings.GITLAB_BASE_URL))
    
    async def from_github(github_event: dict, review_details: List[Dict[str, Any]]) -> 'WebhookMessage' :
        if github_event['action'] == 'opened' and github_event['pull_request']:
            event_type = 'pr'
            url = github_event['pull_request']['html_url']
        elif ((github_event['action'] == 'created') or (github_event['action'] == 'submitted')) and github_event['comment']:
            event_type = 'comment'
            url = github_event['comment']['html_url']
        else:
            event_type = 'none'
            url = github_event['repository']['html_url']

        return WebhookMessage(title=f"{github_event['repository']['full_name']}",
                              project_name=github_event['repository']['name'],
                              event_type = EventType.get_type(event_type),
                              actor_name = github_event['sender']['login'],
                              reviewers = ', '.join(review_detail.get('member_name', '') for review_detail in review_details),
                              review_id = github_event.get('pull_request', {}).get('id', "#0"),
                              new_state = github_event.get('action', None),
                              comment = github_event.get('comment', {}).get('body', None),
                              url=url)