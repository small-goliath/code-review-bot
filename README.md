# 🤖 AI Code Review Notifier

Upsource 또는 GitHub에서 리뷰(혹은 Pull Request)가 생성되면 자동으로 Google Chat 또는 Slack에 알림을 전송하고, OpenAI를 활용해 코드 리뷰를 제공하는 FastAPI 기반의 백엔드 프로젝트입니다.

---

## 📌 주요 기능

- **Upsource 리뷰 감지**
  - Upsource의 Webhook 이벤트를 통해 리뷰 생성 시점 감지
  - 알림 채널(Google Chat, Slack) 알림
  - 변경된 파일을 수집하고 AI 코드 리뷰 수행

- **GitHub PR 감지**
  - GitHub Webhook을 통해 Pull Request 생성 이벤트 수신
  - PR에서 변경된 코드 기반으로 AI 리뷰 수행 및 알림 전송

- **AI 코드 리뷰 자동화**
  - OpenAI GPT 모델을 통해 코드 변경 내용을 분석
  - 리뷰 코멘트를 자동 생성하고, 해당 플랫폼(Upsource, GitHub)에 등록 가능

- **Notification 연동**
  - Google Chat 또는 Slack Webhook을 사용하여 실시간 리뷰 알림 전송

---

## ⚙️ 사용 기술 및 라이브러리

| 구분         | 기술 및 버전           |
|--------------|------------------------|
| 언어         | Python 3.x             |
| 웹 프레임워크 | FastAPI 0.115.12       |
| 비동기 서버  | uvicorn 0.34.1 |
| AI 분석      | OpenAI API 1.73.0 (GPT) |
| HTTP 통신    | httpx 0.28.1           |
| 알림 시스템  | Google Chat, Slack     |
| 코드 리뷰 플랫폼 | Upsource  |

---

## 🔧 환경 변수 설정 (`.env`)

`sample.env` 파일을 참고하여 설정합니다.

```env
REVIEW_TOOL=upsource  # 또는 github

# 공통
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4
REVIEW_FILES=py,kt,java

# Upsource 전용
CODE_REVIEW_BASE_URL=https://upsource.xxx.xxx
CODE_REVIEW_TOOL_ACCOUNT_USERNAME=
CODE_REVIEW_TOOL_ACCOUNT_PASSWORD=

# Notification
WEBHOOK_URI=https://chat.googleapis.com/...
````

---

# 🚀 실행 방법
<pre>
# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행
uvicorn app.main:app --reload --env-file .env --log-config logging.conf
</pre>