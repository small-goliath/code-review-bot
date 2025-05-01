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
    
    async def generate_structor_output_code_review_by_diff(self, file_name: str, diff: str):
        self.log.info("리뷰 중...")
        prompt = f"""
            아래 코드는 특정 파일의 몇 번 라인의 코드가 어떻게 변경되었는지에 대한 내용을 다루고있어.
            해당 내용을 보고 한국어로 코드리뷰해줘.
            
            `{file_name}`
            ```
            {diff}
            ```

            요구사항:
            1. json형식에 맞게 줄바꿈은 하지말고 한 줄로 응답해줘.
            2. `path`필드에는 `코드리뷰한 파일`을 주고 `start_line`필드에는 `코드 라인`을 주고 `body`필드에는 `리뷰내용`을 줘.
            3. `value`값에 대해서 따옴표(')를 포함한다면 따옴표를 백틱으로 대체해.
            4. `value`값에 대해서 쌍따옴표(")를 포함하고 있다면 쌍따옴표 앞에 역슬래시 두 개만 붙여.
            5. `value`값에 대해서 백틱을 포함하고 있다면 백틱 앞에는 역슬래시를 붙이지 마.
            6. `value`값에 대해서 중괄호를 포함하고 있다면 중괄호 앞에 역슬래시를 하나만 붙여.
            7. 하나의 파일에서 여러 군데 수정이 필요하면 json array 형식으로 줘. 
            """
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        self.log.debug(f"prompt {response.usage.prompt_tokens} tokens, completion {response.usage.completion_tokens} tokens: 총 {response.usage.total_tokens} tokens 사용")
        return response.choices[0].message.content