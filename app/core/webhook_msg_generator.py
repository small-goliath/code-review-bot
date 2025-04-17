import requests
from typing import Dict, Any
from app.config import settings

async def review_created_feed_event(review: Dict[str, Any]) -> Dict[str, Any]:
    reviewers = ', '.join(user['userName'] for user in review.get('data', {}).get('base', {}).get('userIds', []))

    try:
        response = requests.post(
            f"{settings.UPSOURCE_BASE_URL}/~rpc/getReviewDetails",
            auth=(settings.UPSOURCE_ACCOUNT_USERNAME, settings.UPSOURCE_ACCOUNT_PASSWORD),
            json={
                "projectId": review['projectId'],
                "reviewId": review['data']['base']['reviewId']
            }
        )
        response.raise_for_status()
        body = response.json()
        title = body['result']['title']

        return {
            "text": f"*{review['data']['base']['actor']['userName']}*님이 리뷰를 생성하였습니다: *{title}* ({review['data']['base']['reviewId']})",
            "attachments": [
                {
                    "fallback": f"*{review['data']['base']['actor']['userName']}*님이 리뷰를 생성하였습니다: *{title}* ({review['data']['base']['reviewId']})",
                    "fields": [
                        {
                            "title": "Project",
                            "value": review['projectId'],
                            "short": True
                        },
                        {
                            "title": "Participant(s)",
                            "value": reviewers,
                            "short": True
                        },
                        {
                            "title": "link",
                            "value": f"<{settings.UPSOURCE_BASE_URL}/{review['projectId']}/review/{review['data']['base']['reviewId']}>"
                        }
                    ],
                    "color": "#F35A00"
                }
            ]
        }
    except requests.RequestException as e:
        raise Exception(f"Error fetching review details: {e}")
    
async def review_state_changed_feed_event(review: Dict[str, Any]) -> Dict[str, Any]:
    review_state = {
        0: '_Open_',
        1: '_Closed_'
    }

    def get_color(new_state: int) -> str:
        return '#F35A00' if new_state == 0 else '#2AB27B'

    try:
        response = requests.post(
            f"{settings.UPSOURCE_BASE_URL}/~rpc/getReviewDetails",
            auth=(settings.UPSOURCE_ACCOUNT_USERNAME, settings.UPSOURCE_ACCOUNT_PASSWORD),
            json={
                "projectId": review['projectId'],
                "reviewId": review['data']['base']['reviewId']
            }
        )
        response.raise_for_status()
        body = response.json()
        title = body['result']['title']

        return {
            "text": f"리뷰 상태가 {review_state[review['data']['oldState']]}에서 {review_state[review['data']['newState']]}로 변경되었습니다: *{title}* ({review['data']['base']['reviewId']})",
            "attachments": [
                {
                    "fallback": f"리뷰 상태가 {review_state[review['data']['oldState']]}에서 {review_state[review['data']['newState']]}로 변경되었습니다: *{title}* ({review['data']['base']['reviewId']})",
                    "fields": [
                        {
                            "title": "Project",
                            "value": review['projectId'],
                            "short": True
                        },
                        {
                            "title": "Changed by",
                            "value": review['data']['base']['actor']['userName'],
                            "short": True
                        },
                        {
                            "title": "link",
                            "value": f"<{settings.UPSOURCE_BASE_URL}/{review['projectId']}/review/{review['data']['base']['reviewId']}>"
                        }
                    ],
                    "color": get_color(review['data']['newState'])
                }
            ]
        }
    except requests.RequestException as e:
        raise Exception(f"Error fetching review details: {e}")
    
async def participant_state_changed_feed_event(review: Dict[str, Any]) -> Dict[str, Any]:
    reviewers = ', '.join(user['userName'] for user in review.get('data', {}).get('base', {}).get('userIds', []))
    review_state = {
        0: '_Unread_',
        1: '_Read_',
        2: '_Accepted_',
        3: '_Rejected_'
    }

    def get_color(new_state: int) -> str:
        return '#F35A00' if new_state == 3 else '#2AB27B'

    participant = review['data']['participant'].get('userName', review['data']['participant'].get('userId'))

    try:
        response = requests.post(
            f"{settings.UPSOURCE_BASE_URL}/~rpc/getReviewDetails",
            auth=(settings.UPSOURCE_ACCOUNT_USERNAME, settings.UPSOURCE_ACCOUNT_PASSWORD),
            json={
                "projectId": review['projectId'],
                "reviewId": review['data']['base']['reviewId']
            }
        )
        response.raise_for_status()
        body = response.json()
        title = body['result']['title']

        return {
            "text": f"{participant}님이 {review_state[review['data']['oldState']]}에서 {review_state[review['data']['newState']]}로 변경하였습니다: *{title}* ({review['data']['base']['reviewId']})",
            "attachments": [
                {
                    "fallback": f"{participant}님이 {review_state[review['data']['oldState']]}에서 {review_state[review['data']['newState']]}로 변경하였습니다: *{title}* ({review['data']['base']['reviewId']})",
                    "fields": [
                        {
                            "title": "Project",
                            "value": review['projectId'],
                            "short": True
                        },
                        {
                            "title": "Participant(s)",
                            "value": reviewers,
                            "short": True
                        },
                        {
                            "title": "link",
                            "value": f"<{settings.UPSOURCE_BASE_URL}/{review['projectId']}/review/{review['data']['base']['reviewId']}>"
                        }
                    ],
                    "color": get_color(review['data']['newState'])
                }
            ]
        }
    except requests.RequestException as e:
        raise Exception(f"Error fetching review details: {e}")
    
async def discussion_feed_event(review: Dict[str, Any]) -> Dict[str, Any]:
    reviewers = ', '.join(user['userName'] for user in review.get('data', {}).get('base', {}).get('userIds', []))

    try:
        response = requests.post(
            f"{settings.UPSOURCE_BASE_URL}/~rpc/getReviewDetails",
            auth=(settings.UPSOURCE_ACCOUNT_USERNAME, settings.UPSOURCE_ACCOUNT_PASSWORD),
            json={
                "projectId": review['projectId'],
                "reviewId": review['data']['base']['reviewId']
            }
        )
        response.raise_for_status()

        url = f"{settings.UPSOURCE_BASE_URL}/{review['projectId']}"
        if 'reviewId' in review['data']['base']:
            url += f"/review/{review['data']['base']['reviewId']}"

        return {
            "text": f"*{review['data']['base']['actor']['userName']}*님이 댓글을 작성했습니다: *{review.get('projectId', '')}*",
            "attachments": [
                {
                    "fallback": f"*{review['data']['base']['actor']['userName']}*님이 댓글을 작성했습니다: *{review.get('projectId', '')}*",
                    "fields": [
                        {
                            "title": "Project",
                            "value": review['projectId'],
                            "short": True
                        },
                        {
                            "title": "Participant(s)",
                            "value": reviewers,
                            "short": True
                        },
                        {
                            "title": "Comment",
                            "value": review['data']['commentText']
                        },
                        {
                            "title": "link",
                            "value": f"<{url}>"
                        }
                    ],
                    "color": "#3AA3E3"
                }
            ]
        }
    except requests.RequestException as e:
        raise Exception(f"Error fetching review details: {e}")