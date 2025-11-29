"""LLM Provider Integrations - Modular and Fast"""
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Base class for all LLM providers"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.name = self.__class__.__name__.replace('Provider', '')

    @abstractmethod
    def chat(self, prompt: str, stream: bool = False) -> str:
        """Send prompt and get response"""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider is properly configured"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI (GPT) Provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        super().__init__(api_key, model)
        self.client = None
        if self.is_configured():
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, prompt: str, stream: bool = False) -> str:
        if not self.client:
            return "❌ OpenAI not configured. Add API key in sidebar."

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ OpenAI Error: {str(e)}"


class ClaudeProvider(LLMProvider):
    """Anthropic Claude Provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.client = None
        if self.is_configured():
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Claude: {e}")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, prompt: str, stream: bool = False) -> str:
        if not self.client:
            return "❌ Claude not configured. Add API key in sidebar."

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"❌ Claude Error: {str(e)}"


class GeminiProvider(LLMProvider):
    """Google Gemini Provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
        super().__init__(api_key, model)
        self.client = None
        if self.is_configured():
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, prompt: str, stream: bool = False) -> str:
        if not self.client:
            return "❌ Gemini not configured. Add API key in sidebar."

        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Gemini Error: {str(e)}"


class OllamaProvider(LLMProvider):
    """Ollama (Local LLM) Provider - FREE"""

    def __init__(self, api_key: Optional[str] = None, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        super().__init__(api_key, model)
        self.base_url = base_url

    def is_configured(self) -> bool:
        """Check if Ollama is running"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def chat(self, prompt: str, stream: bool = False) -> str:
        if not self.is_configured():
            return "❌ Ollama not running. Start with: ollama serve"

        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=60
            )
            if response.status_code == 200:
                return response.json().get('response', 'No response')
            else:
                return f"❌ Ollama Error: {response.status_code}"
        except Exception as e:
            return f"❌ Ollama Error: {str(e)}"


def get_all_providers(config: Dict[str, Any]) -> Dict[str, LLMProvider]:
    """Initialize all configured providers"""
    providers = {}

    # OpenAI
    if config.get('openai_key'):
        providers['OpenAI'] = OpenAIProvider(
            api_key=config['openai_key'],
            model=config.get('openai_model', 'gpt-4o-mini')
        )

    # Claude
    if config.get('claude_key'):
        providers['Claude'] = ClaudeProvider(
            api_key=config['claude_key'],
            model=config.get('claude_model', 'claude-3-5-sonnet-20241022')
        )

    # Gemini
    if config.get('gemini_key'):
        providers['Gemini'] = GeminiProvider(
            api_key=config['gemini_key'],
            model=config.get('gemini_model', 'gemini-2.0-flash-exp')
        )

    # Ollama (always try, it's free)
    ollama = OllamaProvider(model=config.get('ollama_model', 'llama3.2'))
    if ollama.is_configured():
        providers['Ollama'] = ollama

    return providers
