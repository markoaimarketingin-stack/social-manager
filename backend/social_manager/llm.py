"""
LLM layer with structured outputs, JSON schema validation, and retrieval.
Provider-agnostic design; using Groq as the LLM provider.
"""

from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()
import json
import asyncio
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel, ValidationError

try:
    from groq import Groq
except Exception:
    Groq = None

MODEL_NAME = "llama-3.1-8b-instant"


class StructuredOutputValidator:
    @staticmethod
    def validate(output: str, schema: Type[BaseModel]) -> BaseModel:
        if "```json" in output:
            json_str = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output:
            json_str = output.split("```")[1].split("```")[0].strip()
        else:
            json_str = output
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in LLM output: {e}")
        return schema(**data)

    @staticmethod
    def get_json_schema(model: Type[BaseModel]) -> Dict:
        return model.model_json_schema()


class RetryStrategy:
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay

    async def execute(self, fn, *args, **kwargs):
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await fn(*args, **kwargs) if asyncio.iscoroutinefunction(fn) else fn(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_attempts:
                    raise
                delay = self.base_delay * (2 ** (attempt - 1))
                print(f"Retry attempt {attempt}/{self.max_attempts} after {delay}s: {e}")
                await asyncio.sleep(delay)


class BrandVoiceRetrieval:
    def __init__(self):
        self.brand_guides: Dict[str, str] = {}
        self.style_guides: Dict[str, str] = {}

    def register_brand_voice(self, brand_name: str, voice_description: str):
        self.brand_guides[brand_name] = voice_description

    def register_style_guide(self, platform: str, guide: str):
        self.style_guides[platform] = guide

    def get_system_context(self, brand=None, platform=None) -> str:
        parts = []
        if brand and brand in self.brand_guides:
            parts.append(f"## Brand Voice\n{self.brand_guides[brand]}")
        if platform and platform in self.style_guides:
            parts.append(f"## {platform} Style Guide\n{self.style_guides[platform]}")
        return "\n\n".join(parts)


class GroqClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.available = False
        self.validator = StructuredOutputValidator()
        self.retry_strategy = RetryStrategy(max_attempts=3, base_delay=1.0)
        self.brand_retrieval = BrandVoiceRetrieval()
        self._client = None
        if Groq and self.api_key:
            try:
                self._client = Groq(api_key=self.api_key)
                self.available = True
            except Exception:
                self.available = False

    def generate(self, prompt: str, system_instruction=None) -> str:
        if not self.available:
            return f"[Heuristic fallback due to missing Groq]\n{prompt[:1600]}"
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            response = self._client.chat.completions.create(
                model=MODEL_NAME, messages=messages, max_tokens=2048
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"[Groq error: {e}]\n{prompt[:1600]}"

    async def generate_structured(self, prompt: str, output_schema: Type[BaseModel], system_instruction=None):
        schema_json = self.validator.get_json_schema(output_schema)
        enhanced_prompt = f"""{prompt}\n\n# Output Format\nReturn valid JSON matching this schema:\n{json.dumps(schema_json, indent=2)}\n\nRespond with ONLY the JSON, no explanation."""
        async def llm_call():
            return self.validator.validate(self.generate(enhanced_prompt, system_instruction), output_schema)
        return await self.retry_strategy.execute(llm_call)

    def set_brand_voice(self, brand_name: str, description: str):
        self.brand_retrieval.register_brand_voice(brand_name, description)

    def set_style_guide(self, platform: str, guide: str):
        self.brand_retrieval.register_style_guide(platform, guide)

    def get_enriched_system_instruction(self, brand=None, platform=None) -> str:
        return self.brand_retrieval.get_system_context(brand, platform)


client = GroqClient()
GeminiClient = GroqClient
