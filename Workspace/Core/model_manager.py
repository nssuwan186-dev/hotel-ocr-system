# Core/model_manager.py
"""
จัดการโมเดล AI หลายตัว: Gemini, OpenAI, Claude, Ollama
"""

import os
import yaml
import asyncio
import aiohttp
import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    GOOGLE = "google"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


@dataclass
class ModelConfig:
    name: str
    provider: ModelProvider
    model_id: str
    api_key: Optional[str]
    base_url: str
    max_tokens: int
    temperature: float
    capabilities: Dict[str, bool]
    thai_optimized: bool
    cost_per_1k_input: float
    cost_per_1k_output: float
    priority: int
    rate_limit: int = 15
    requires_internet: bool = True


class ModelManager:
    def __init__(self, config_path: str = "Workspace/Config/models.yaml"):
        self.config_path = config_path
        self.models: Dict[str, ModelConfig] = {}
        self.active_model: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_counts: Dict[str, int] = {}
        self.load_config()

    def load_config(self):
        """โหลดการตั้งค่าโมเดลจาก YAML"""
        try:
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"Config not found: {self.config_path}")
                return

            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            self.default_model = config.get("default_model", "gemini-2.0-flash")
            self.fallback_config = config.get("fallback", {})

            for name, model_data in config.get("models", {}).items():
                api_key_env = model_data.get("api_key_env", "")
                api_key = os.getenv(api_key_env) if api_key_env else None

                self.models[name] = ModelConfig(
                    name=name,
                    provider=ModelProvider(model_data["provider"]),
                    model_id=model_data["model_id"],
                    api_key=api_key,
                    base_url=model_data.get("base_url", ""),
                    max_tokens=model_data["max_tokens"],
                    temperature=model_data["temperature"],
                    capabilities=model_data.get("capabilities", {}),
                    thai_optimized=model_data.get("thai_optimized", False),
                    cost_per_1k_input=model_data.get("cost_per_1k_input", 0),
                    cost_per_1k_output=model_data.get("cost_per_1k_output", 0),
                    priority=model_data.get("priority", 99),
                    rate_limit=model_data.get("rate_limit_per_minute", 15),
                    requires_internet=model_data.get("requires_internet", True),
                )
                self.request_counts[name] = 0

            self.active_model = self.default_model
            logger.info(
                f"Loaded {len(self.models)} models. Default: {self.default_model}"
            )

        except Exception as e:
            logger.error(f"Failed to load model config: {e}")
            raise

    async def init_session(self):
        """เริ่มต้น HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60)
            )

    async def close(self):
        """ปิดการเชื่อมต่อ"""
        if self.session and not self.session.closed:
            await self.session.close()

    def get_model(self, name: Optional[str] = None) -> ModelConfig:
        """ดึงข้อมูลโมเดล"""
        model_name = name or self.active_model
        if model_name not in self.models:
            logger.warning(f"Model {model_name} not found, using default")
            model_name = self.default_model
        return self.models.get(model_name, self.models.get(self.default_model))

    def select_model_for_task(
        self,
        task_type: str,
        complexity: str = "low",
        requires_vision: bool = False,
        thai_required: bool = True,
        economy_mode: bool = False,
    ) -> str:
        """
        เลือกโมเดลที่เหมาะสมกับงานอัตโนมัติ
        """
        candidates = []

        for name, config in self.models.items():
            score = 0

            if requires_vision and not config.capabilities.get("vision"):
                continue

            if thai_required and not config.thai_optimized:
                score -= 5

            score += 100 - config.priority

            if complexity == "high" and config.max_tokens > 8000:
                score += 10

            if economy_mode:
                score += (1.0 / (config.cost_per_1k_input + 0.001)) * 10

            if self.request_counts.get(name, 0) >= config.rate_limit:
                continue

            candidates.append((name, score, config))

        if not candidates:
            for name, config in self.models.items():
                if config.provider == ModelProvider.OLLAMA:
                    return name
            return self.default_model

        candidates.sort(key=lambda x: x[1], reverse=True)
        selected = candidates[0][0]

        logger.info(f"Selected model {selected} for task {task_type}")
        return selected

    async def generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        image_path: Optional[str] = None,
        image_base64: Optional[str] = None,
        json_mode: bool = False,
    ) -> Dict[str, Any]:
        """สร้างข้อความจากโมเดลที่เลือก"""
        await self.init_session()

        model = self.get_model(model_name)
        self.request_counts[model.name] += 1

        image_data = None
        if image_path:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
        elif image_base64:
            image_data = image_base64.replace("data:image/jpeg;base64,", "")

        try:
            if model.provider == ModelProvider.GOOGLE:
                return await self._call_gemini(model, prompt, image_data, json_mode)
            elif model.provider == ModelProvider.OPENAI:
                return await self._call_openai(model, prompt, image_data, json_mode)
            elif model.provider == ModelProvider.ANTHROPIC:
                return await self._call_claude(model, prompt, image_data)
            elif model.provider == ModelProvider.OLLAMA:
                return await self._call_ollama(model, prompt)
            else:
                raise ValueError(f"Unknown provider: {model.provider}")

        except Exception as e:
            logger.error(f"Error calling {model.name}: {e}")
            return await self._handle_error(e, model, prompt, image_data, json_mode)

    async def _call_gemini(
        self,
        model: ModelConfig,
        prompt: str,
        image_data: Optional[str],
        json_mode: bool,
    ) -> Dict[str, Any]:
        """เรียก Google Gemini API"""
        url = f"{model.base_url}/models/{model.model_id}:generateContent"

        headers = {"Content-Type": "application/json"}
        if model.api_key:
            headers["x-goog-api-key"] = model.api_key

        contents = [{"parts": [{"text": prompt}]}]

        if image_data:
            contents[0]["parts"].append(
                {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
            )

        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": model.temperature,
                "maxOutputTokens": model.max_tokens,
                "topP": 0.95,
            },
        }

        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"

        async with self.session.post(url, headers=headers, json=body) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Gemini API error {resp.status}: {text}")

            data = await resp.json()
            text_response = data["candidates"][0]["content"]["parts"][0]["text"]

            return {
                "text": text_response,
                "model": model.name,
                "usage": data.get("usageMetadata", {}),
            }

    async def _call_openai(
        self,
        model: ModelConfig,
        prompt: str,
        image_data: Optional[str],
        json_mode: bool,
    ) -> Dict[str, Any]:
        """เรียก OpenAI API"""
        url = f"{model.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {model.api_key}",
            "Content-Type": "application/json",
        }

        messages = [{"role": "user", "content": prompt}]

        if image_data:
            messages[0]["content"] = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                },
            ]

        body = {
            "model": model.model_id,
            "messages": messages,
            "temperature": model.temperature,
            "max_tokens": model.max_tokens,
        }

        if json_mode:
            body["response_format"] = {"type": "json_object"}

        async with self.session.post(url, headers=headers, json=body) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"OpenAI API error {resp.status}: {text}")

            data = await resp.json()
            text_response = data["choices"][0]["message"]["content"]

            return {
                "text": text_response,
                "model": model.name,
                "usage": data.get("usage", {}),
            }

    async def _call_claude(
        self, model: ModelConfig, prompt: str, image_data: Optional[str]
    ) -> Dict[str, Any]:
        """เรียก Anthropic Claude API"""
        url = f"{model.base_url}/messages"

        headers = {
            "x-api-key": model.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        content = [{"type": "text", "text": prompt}]

        if image_data:
            content.insert(
                0,
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
            )

        body = {
            "model": model.model_id,
            "max_tokens": model.max_tokens,
            "temperature": model.temperature,
            "messages": [{"role": "user", "content": content}],
        }

        async with self.session.post(url, headers=headers, json=body) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"Claude API error {resp.status}: {text}")

            data = await resp.json()
            text_response = data["content"][0]["text"]

            return {
                "text": text_response,
                "model": model.name,
                "usage": data.get("usage", {}),
            }

    async def _call_ollama(self, model: ModelConfig, prompt: str) -> Dict[str, Any]:
        """เรียก Local Ollama"""
        url = f"{model.base_url}/api/generate"

        body = {
            "model": model.model_id,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": model.temperature,
                "num_predict": model.max_tokens,
            },
        }

        try:
            async with self.session.post(url, json=body) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"Ollama error {resp.status}: {text}")

                data = await resp.json()

                return {
                    "text": data.get("response", ""),
                    "model": model.name,
                    "usage": {
                        "input_tokens": data.get("prompt_eval_count", 0),
                        "output_tokens": data.get("eval_count", 0),
                    },
                }
        except aiohttp.ClientConnectorError:
            raise Exception(f"Cannot connect to Ollama at {model.base_url}")

    async def _handle_error(
        self,
        error: Exception,
        original_model: ModelConfig,
        prompt: str,
        image_data: Optional[str],
        json_mode: bool,
    ) -> Dict[str, Any]:
        """จัดการ error ด้วย fallback chain"""
        logger.warning(f"Error with {original_model.name}: {error}")

        fallback_order = ["gemini-1.5-flash", "gpt-4o-mini", "llama3.2-local"]

        for fallback_name in fallback_order:
            if fallback_name == original_model.name:
                continue
            if fallback_name not in self.models:
                continue
            if image_data and not self.models[fallback_name].capabilities.get("vision"):
                continue

            try:
                logger.info(f"Trying fallback: {fallback_name}")
                result = await self.generate(
                    prompt, fallback_name, None, image_data, json_mode
                )
                result["fallback_used"] = True
                result["original_error"] = str(error)
                return result
            except Exception as e:
                continue

        return {
            "error": True,
            "message": f"All models failed: {error}",
            "fallback_used": False,
        }

    def get_usage_stats(self) -> Dict[str, Any]:
        """สถิติการใช้งาน"""
        return {
            "request_counts": self.request_counts,
            "active_model": self.active_model,
            "available_models": list(self.models.keys()),
        }

    def is_offline_available(self) -> bool:
        """ตรวจสอบว่ามี local model พร้อมใช้งาน"""
        for config in self.models.values():
            if config.provider == ModelProvider.OLLAMA:
                return True
        return False
