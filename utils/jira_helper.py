# utils/jira_helper.py

import logging

import requests
from requests.auth import HTTPBasicAuth

from config.jira_config import (
    JIRA_URL,
    JIRA_EMAIL,
    JIRA_API_TOKEN,
    JIRA_PROJECT_KEY,
    DEFAULT_API_TIMEOUT
)

# ── Logger 설정 ───────────────────────────────────────────────────

logger = logging.getLogger(__name__)

# ── Jira Bug 생성 ────────────────────────────────────────────────

def create_jira_bug_ticket(summary, description):

    url = f"{JIRA_URL}/rest/api/2/issue"

    auth = HTTPBasicAuth(
        JIRA_EMAIL,
        JIRA_API_TOKEN
    )

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "fields": {
            "project": {
                "key": JIRA_PROJECT_KEY
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": "버그"
            },
            "labels": [
                "Automation"
            ]
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=auth,
            timeout=DEFAULT_API_TIMEOUT
        )

        if response.status_code == 201:

            issue_key = response.json().get("key")

            logger.info(
                f"Jira 티켓 생성 성공: "
                f"{JIRA_URL}/browse/{issue_key}"
            )

            return issue_key

        else:

            logger.error(
                f"Jira 생성 실패: "
                f"{response.status_code}, "
                f"{response.text}"
            )

            return None

    except Exception as e:

        logger.error(f"Jira 통신 오류: {e}")

        return None

# ── Jira 스크린샷 첨부 ────────────────────────────────────────────

def attach_image_to_jira(issue_key, image_bytes):

    url = (
        f"{JIRA_URL}/rest/api/2/issue/"
        f"{issue_key}/attachments"
    )

    auth = HTTPBasicAuth(
        JIRA_EMAIL,
        JIRA_API_TOKEN
    )

    headers = {
        "X-Atlassian-Token": "no-check"
    }

    files = {
        "file": (
            "error_screenshot.png",
            image_bytes,
            "image/png"
        )
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            auth=auth,
            files=files,
            timeout=DEFAULT_API_TIMEOUT + 10
        )

        if response.status_code == 200:

            logger.info(
                "스크린샷 첨부 성공"
            )

        else:

            logger.error(
                f"스크린샷 첨부 실패: "
                f"{response.status_code}, "
                f"{response.text}"
            )

    except Exception as e:

        logger.error(
            f"스크린샷 첨부 오류: {e}"
        )


# ── 기존 이슈에 코멘트 추가 ────────────────────────────────────────

def add_comment_to_issue(issue_key, body):

    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}/comment"

    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url,
            json={"body": body},
            headers=headers,
            auth=auth,
            timeout=DEFAULT_API_TIMEOUT
        )

        if response.status_code == 201:
            logger.info(f"코멘트 추가 성공: {issue_key}")
        else:
            logger.error(
                f"코멘트 추가 실패: {response.status_code}, {response.text}"
            )

    except Exception as e:
        logger.error(f"코멘트 추가 오류: {e}")


# ── 이슈 상태 전이 ────────────────────────────────────────────────

_DONE_TRANSITION_NAMES = {"done", "완료", "resolved", "closed", "close", "resolve"}


def _get_done_transition_id(issue_key):
    """이슈에서 사용 가능한 transitions 중 Done/완료 계열 ID를 반환"""

    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}/transitions"

    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

    try:
        response = requests.get(
            url,
            auth=auth,
            timeout=DEFAULT_API_TIMEOUT
        )

        if response.status_code != 200:
            logger.error(f"transitions 조회 실패: {response.status_code}")
            return None

        for t in response.json().get("transitions", []):
            if t["name"].lower() in _DONE_TRANSITION_NAMES:
                return t["id"]

        logger.warning(f"{issue_key}: Done 계열 transition 없음")
        return None

    except Exception as e:
        logger.error(f"transitions 조회 오류: {e}")
        return None


def transition_issue_to_done(issue_key):
    """이슈를 Done/완료 상태로 전이. 전이 불가 시 로그만 남기고 무시."""

    transition_id = _get_done_transition_id(issue_key)

    if not transition_id:
        return

    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}/transitions"

    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url,
            json={"transition": {"id": transition_id}},
            headers=headers,
            auth=auth,
            timeout=DEFAULT_API_TIMEOUT
        )

        if response.status_code == 204:
            logger.info(f"이슈 Done 전이 성공: {issue_key}")
        else:
            logger.error(
                f"이슈 전이 실패: {response.status_code}, {response.text}"
            )

    except Exception as e:
        logger.error(f"이슈 전이 오류: {e}")