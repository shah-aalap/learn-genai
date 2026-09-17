import os
from pathlib import Path
from typing import Self
from google import genai
from example_lib import ExampleClass


class MainClass(ExampleClass):
    def __init__(self, config_path: str | Path) -> None:
        super().__init__(config=config_path)
        self._gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "NotSet"))
        self._gemini_model = self._config["gemini_model"]
        self._l.info(f"Using Gemini model '{self._gemini_model}'")

    def run(self) -> Self:
        if self._config["mode"] == "text":
            self._generate_text()
        else:  # stream
            self._generate_stream()
        return self

    def _generate_text(self) -> Self:
        self._l.info(f"Generating non-streaming content")
        question = "Explain quantum computing in one short sentence."
        response = self._gemini_client.models.generate_content(
            model=self._gemini_model,
            contents=question,
        )
        self._l.info(f"Question: {question}")
        self._l.info(f"Response: {response.text}")
        return self

    # 3. Make a streaming text generation call (for real-time responses)
    def _generate_stream(self) -> Self:
        self._l.info(f"Generating streaming content")
        question = "Write a short poem about a robot learning to paint."
        response_stream = self._gemini_client.models.generate_content_stream(
            model=self._gemini_model,
            contents=question,
        )
        self._l.info(f"Question: {question}")
        for chunk in response_stream:
            self._l.info(f"Response chunk: {chunk.text}")
        return self
