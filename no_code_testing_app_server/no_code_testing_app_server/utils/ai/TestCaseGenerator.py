from huggingface_hub import InferenceClient
from typing import Optional, Dict, Any
# from .vector import retriever
from no_code_testing_app_server.patterns.Singleton import singleton
import json
import os
from dotenv import load_dotenv
load_dotenv()


@singleton
class TestCaseGenerator:
    def __init__(self):
        self.client = InferenceClient(
            api_key=os.getenv('HUGGING_FACES_API_KEY'))
        self._init_prompt()

    def _generate_response(self, prompt):
        response = self.client.chat_completion(
            model="Qwen/Qwen3-Coder-480B-A35B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.1
        )

        return response.choices[0].message.content

    def _init_prompt(self):
        self.base_prompt = """
            You are a strict test automation engineer. Generate ONLY a VALID JSON object with:
            - "test_case_name": A short descriptive name for the test case
            - "components": {{ "comp_1": {{...}}, "comp_2": {{...}}, ... }}
            - Each component key MUST follow the format comp_N (starting at comp_1).
            - Each value MUST contain: name, action, type, and required fields depending on the action.
            - "dependencies": [{{"from": "comp_X", "to": "comp_Y", "type": "DEPENDENCY"}}]

            ### RULES (MUST FOLLOW):
            1. OUTPUT ONLY JSON. NO MARKDOWN, COMMENTS, OR EXTRA TEXT.
            2. Component keys: comp_1, comp_2, ... in sequential order.
            3. Locator priority: id > name > class name > xpath
            4. DEPENDENCIES (STRICT ORDER):
            - Every find_element MUST depend on the most recent get (navigation) component.
            - Every send_keys, click, or assert_* MUST depend on the immediately preceding find_element component.
            - DO NOT create extra dependencies. Only use "DEPENDENCY".
            5. Required fields:
            - get: needs "url" and "timeout": 10
            - find_element: needs "locator" and "locator_type"
            - send_keys: needs "value"
            - assert_*: needs "value"
            6. DO NOT invent elements. Use only those visible in HTML.
            7. If no matching element, skip or use safe fallback (e.g., xpath with //button[text()='Login']).
            8. Never include "index" unless necessary.
            9. The "type" field MUST be:
            - get → "navigation"
            - find_element → "element_lookup"
            - send_keys → "input_action"
            - click / assert_* → "interaction"

            ### PAGE CONTEXT:
            URL: {page_url}
            HTML (body): {page_html}

            ### EXAMPLES OF ORDERED DEPENDENCIES:
            "components": {{
                "comp_1": {{ "name": "Open Login Page", "action": "get", "type": "navigation", "url": "https://example.com/login", "timeout": 10 }},
                "comp_2": {{ "name": "Find Username Field", "action": "find_element", "type": "element_lookup", "locator": "username", "locator_type": "id" }},
                "comp_3": {{ "name": "Enter Username", "action": "send_keys", "type": "input_action", "value": "testuser" }}
            }},
            "dependencies": [
                {{"from": "comp_1", "to": "comp_2", "type": "DEPENDENCY"}},
                {{"from": "comp_2", "to": "comp_3", "type": "DEPENDENCY"}}
            ]

            ### TASK:
            {task}

            ### OUTPUT (JSON only):
        """

    def generate_test_case(self, user_prompt: str, html_content: str, page_url: str, examples):
        prompt = self.base_prompt.format(
            page_url=page_url,
            page_html=html_content,
            examples=examples,
            task=user_prompt
        )
        return self._generate_response(prompt)

    def run(self, user_prompt: str, html_content: str, page_url: str) -> Optional[Dict[str, Any]]:
        # examples = retriever.invoke(user_prompt)
        test_case = self.generate_test_case(
            user_prompt, [], html_content, page_url)

        try:
            parsed_result = json.loads(test_case)
            print("Parsed JSON:", parsed_result)
            return parsed_result
        except json.JSONDecodeError as e:
            print("Failed to parse JSON:", e)
            print("Raw result:", test_case)
