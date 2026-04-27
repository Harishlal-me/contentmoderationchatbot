from src.llm_handler import LLMHandler
handler = LLMHandler()
for chunk in handler.generate_response([{"role": "user", "content": "analyze this text"}], system_override="analyze"):
    pass
