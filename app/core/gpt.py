from app.logger import get_logger
from app.config import settings
from openai import OpenAI

class GPT():
    log = get_logger("openai")
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEYS)

    async def generate_code_review_by_files(self, old_file_name: str, old_file_code: str, new_file_name: str, new_file_code: str):
        self.log.info("리뷰 중...")
        prompt = "아래 코드를 한국어로 코드리뷰해줘."
        if old_file_name is None:
            prompt += f"""
            
            요구사항: 파일명과 코드 라인 넘버를 명시하고 어떤 부분에 대한 리뷰인지 한국어로 리뷰해줘.
            {new_file_name}
            ```
            {new_file_code}
            ```
            """
        else:
            prompt += f"""
            
            `old code`에서 `old code`로 코드가 수정 되었을 때, 한국어로 코드리뷰해줘.
            요구사항: 파일명과 코드 라인 넘버를 명시하고 어떤 부분에 대한 리뷰인지 한국어로 리뷰해줘.
            `{old_file_name}`
            ```
            {old_file_code}
            ```

            `{new_file_name}`
            ```
            {new_file_code}
            ```
            """
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        self.log.debug(f"prompt {response.usage.prompt_tokens} tokens, completion {response.usage.completion_tokens} tokens: 총 {response.usage.total_tokens} tokens 사용")
        return response.choices[0].message.content

    async def generate_code_review_by_diff(self, file_name: str, diff: str):
        self.log.info("리뷰 중...")
        prompt = f"""
            아래 코드는 특정 파일의 몇 번 라인의 코드가 어떻게 변경되었는지에 대한 내용을 다루고있어.
            해당 내용을 보고 한국어로 코드리뷰해줘.
            
            요구사항: 파일명과 코드 라인 넘버를 명시하고 어떤 부분에 대한 리뷰인지 한국어로 리뷰해줘.
            `{file_name}`
            ```
            {diff}
            ```
            """
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        self.log.debug(f"prompt {response.usage.prompt_tokens} tokens, completion {response.usage.completion_tokens} tokens: 총 {response.usage.total_tokens} tokens 사용")
        return response.choices[0].message.content