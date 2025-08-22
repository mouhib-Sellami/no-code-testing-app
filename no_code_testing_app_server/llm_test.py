# import re
# import json
# import requests
# from bs4 import BeautifulSoup
# from langchain_ollama.llms import OllamaLLM
# from langchain_core.prompts import ChatPromptTemplate
# import os
# from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
# from langchain.callbacks.manager import CallbackManager
# import uuid
# from typing import Optional, Dict, Any
# from no_code_testing_app_server.no_code_testing_app_server.utils.vector import retriever


# class StreamingPrintCallbackHandler(StreamingStdOutCallbackHandler):
#     def on_llm_new_token(self, token: str, **kwargs) -> None:
#         print(token, end="", flush=True)


# class TestCaseGenerator:
#     def _init_(self):
#         self.callback_manager = CallbackManager(
#             [StreamingPrintCallbackHandler()])
#         self.model = self._initialize_model()
#         self.model_validation = self._initialize_validation_model()
#         self.prompt, self.prompt_validation = self._initialize_prompts()
#         self.chain = self.prompt | self.model
#         self.validation_chain = self.prompt_validation | self.model_validation
#         self.knowledge_base = self._load_knowledge_base()

#     def _initialize_model(self) -> OllamaLLM:
#         return OllamaLLM(
#             model="qwen3:14b",
#             repeat_penalty=1.2,
#             temperature=0.1,
#             num_ctx=4096,
#             top_k=20,
#             callback_manager=self.callback_manager,
#             streaming=True,
#             keep_alive=True
#         )

#     def _initialize_validation_model(self) -> OllamaLLM:
#         return OllamaLLM(
#             model="qwen2.5:1.5b",
#             callback_manager=self.callback_manager,
#             streaming=True,
#         )

#     def _initialize_prompts(self) -> tuple:
#         test_case_template = """You are a strict test automation engineer. Generate ONLY a VALID JSON object with:
#     - "components": {{"comp_1": {{...}}, "comp_2": {{...}}}} 
#     - Each component key MUST follow the format comp_N (starting at comp_1).
#     - Each value MUST contain: name, action, type, and required fields depending on the action.
#     - "dependencies": [{{"from": "comp_X", "to": "comp_Y", "type": "DEPENDENCY"}}]

#     ### RULES (MUST FOLLOW):
#     1. OUTPUT ONLY JSON. NO MARKDOWN, COMMENTS, OR EXTRA TEXT.
#     2. Component keys: comp_1, comp_2, ... in sequential order.
#     3. Locator priority: id > name > class name > xpath
#     4. DEPENDENCIES:
#     - Every find_element must have DEPENDENCY on the last get action.
#     - Every click, send_keys, assert_* must depend on its preceding find_element.
#     - ONLY use "DEPENDENCY" type, never "RUN_AFTER".
#     5. Required fields:
#     - get: needs "url" and "timeout": 10
#     - find_element: needs "locator" and "locator_type"
#     - send_keys: needs "value"
#     - assert_*: needs "value"
#     6. DO NOT invent elements. Use only those visible in HTML.
#     7. If no matching element, skip or use safe fallback (e.g., xpath with //button[text()='Login']).
#     8. Never include "index" unless necessary.

#     ### PAGE CONTEXT:
#     URL: {page_url}
#     HTML (body): {page_html}

#     ### FEW-SHOT EXAMPLES:
#     {examples}

#     ### TASK:
#     {prompt}

#     ### OUTPUT (JSON only):"""

#         validation_template = """Validate and fix this test case JSON:
#     {data}

#     Rules:
#     1. Components must be numbered sequentially from comp_1
#     2. Required fields must exist per action type
#     3. Locator types must follow priority rules
#     4. Dependencies must use only DEPENDENCY
#     5. Remove any invalid fields

#     Return ONLY the corrected JSON with NO other text."""

#         return (
#             ChatPromptTemplate.from_template(test_case_template),
#             ChatPromptTemplate.from_template(validation_template)
#         )


#     def _load_knowledge_base(self) -> Dict[str, Any]:
#         base_path = os.path.join(os.getcwd(), 'cases.json')
#         if os.path.exists(base_path):
#             try:
#                 with open(base_path, 'r') as f:
#                     return json.load(f)
#             except json.JSONDecodeError:
#                 return {}
#         return {}

#     def extract_first_url(self, text: str) -> Optional[str]:
#         url_pattern = re.compile(
#             r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?')
#         match = url_pattern.search(text)
#         return match.group(0) if match else None

#     def fetch_body_html(self, url: str, timeout: int = 20) -> str:
#         try:
#             # Use selenium to wait for React content to load
#             from selenium import webdriver
#             from selenium.webdriver.chrome.options import Options
#             from selenium.webdriver.common.by import By
#             from selenium.webdriver.support.ui import WebDriverWait
#             from selenium.webdriver.support import expected_conditions as EC
#             import time
            
#             options = Options()
#             options.add_argument("--headless")
#             options.add_argument("--disable-gpu")
#             options.add_argument("--no-sandbox")

#             driver = webdriver.Chrome(options=options)
#             driver.get(url)
#             time.sleep(5)  # Wait for page to load
#             html = driver.page_source
#             driver.quit()

#             soup = BeautifulSoup(html, "html.parser")
#             body = soup.body
#             return str(body) if body else ""

#         except Exception as e:
#             print(f"Error fetching React content: {str(e)}")
#             return ""

#     def extract_and_validate_json(self, text: str) -> Optional[str]:
#         try:
#             json.loads(text)
#             return text
#         except json.JSONDecodeError:
#             json_pattern = r'\{.*\}'
#             match = re.search(json_pattern, text, re.DOTALL)
#             if match:
#                 try:
#                     json_data = json.loads(match.group(0))
#                     return json.dumps(json_data)
#                 except json.JSONDecodeError:
#                     pass
#         return None

#     def generate_test_case(self, page_url: str, user_prompt: str, examples: str) -> Optional[Dict[str, Any]]:
#         page_html = self.fetch_body_html(page_url) if page_url else ""

#         payload = {
#             "prompt": user_prompt,
#             "page_url": page_url,
#             "page_html": page_html,
#             "examples": examples
#         }

#         print("\nGenerating test case...\n")
#         result = str(self.chain.invoke(payload))

#         json_output = self.extract_and_validate_json(result)
#         if not json_output:
#             print("Initial generation failed validation, attempting to fix...")
#             validation_result = str(
#                 self.validation_chain.invoke({"data": result}))
#             json_output = self.extract_and_validate_json(validation_result)

#         if json_output:
#             try:
#                 return json.loads(json_output)
#             except json.JSONDecodeError as e:
#                 print(f"JSON parsing failed: {e}")
#         return None

#     def run(self) -> None:
#         while True:
#             print("\n" + "="*50)
#             page_url = input(
#                 "Enter page URL (or leave blank if none): ").strip()
#             user_prompt = input("Describe test scenario (q to quit): ").strip()

#             if user_prompt.lower() == 'q':
#                 break
#             example = retriever.invoke(user_prompt)
#             test_case = self.generate_test_case(page_url, user_prompt, example)
#             if test_case:
#                 print("\nGenerated Test Case:")
#                 print(json.dumps(test_case, indent=2))
#                 json.dump(test_case, open(f'{str(uuid.uuid4())}.json', 'w'))
#             else:
#                 print("Failed to generate valid test case")


# if __name__ == "__main__":
#     generator = TestCaseGenerator()
#     generator.run()