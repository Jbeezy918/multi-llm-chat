"""LLM Pricing and Token Tracking - Revenue Focused"""
from typing import Dict, Tuple
import tiktoken


# Current pricing as of Nov 2024 (per 1M tokens)
# Source: Official provider pricing pages
PRICING = {
    "openai": {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.150, "output": 0.600},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    },
    "claude": {
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    },
    "gemini": {
        "gemini-2.0-flash-exp": {"input": 0.00, "output": 0.00},  # Free during preview
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    },
    "ollama": {
        "_default": {"input": 0.00, "output": 0.00}  # Free/Local
    }
}


def estimate_tokens(text: str, model: str = "gpt-4o") -> int:
    """Estimate token count for text"""
    try:
        # Use tiktoken for OpenAI models (most accurate)
        if model.startswith("gpt"):
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        else:
            # Rough estimate for other models: ~4 chars per token
            return len(text) // 4
    except Exception:
        # Fallback: rough estimate
        return len(text) // 4


def calculate_cost(input_tokens: int, output_tokens: int, model: str, provider: str) -> float:
    """Calculate cost in USD for given token usage"""
    provider = provider.lower()

    # Get pricing for provider
    if provider not in PRICING:
        return 0.0

    provider_pricing = PRICING[provider]

    # Get model pricing (use default if model not found)
    if model in provider_pricing:
        model_pricing = provider_pricing[model]
    elif "_default" in provider_pricing:
        model_pricing = provider_pricing["_default"]
    else:
        return 0.0

    # Calculate cost (pricing is per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (output_tokens / 1_000_000) * model_pricing["output"]

    return input_cost + output_cost


def get_pricing_info(model: str, provider: str) -> Dict[str, float]:
    """Get pricing info for a model"""
    provider = provider.lower()

    if provider not in PRICING:
        return {"input": 0.0, "output": 0.0}

    provider_pricing = PRICING[provider]

    if model in provider_pricing:
        return provider_pricing[model]
    elif "_default" in provider_pricing:
        return provider_pricing["_default"]
    else:
        return {"input": 0.0, "output": 0.0}


class TokenTracker:
    """Track token usage and costs across session"""

    def __init__(self):
        self.usage = {}  # {provider: {model: {input_tokens, output_tokens, cost}}}
        self.total_cost = 0.0

    def track(self, provider: str, model: str, prompt: str, response: str):
        """Track a single interaction"""
        input_tokens = estimate_tokens(prompt, model)
        output_tokens = estimate_tokens(response, model)
        cost = calculate_cost(input_tokens, output_tokens, model, provider)

        # Initialize provider if needed
        if provider not in self.usage:
            self.usage[provider] = {}

        # Initialize model if needed
        if model not in self.usage[provider]:
            self.usage[provider][model] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0,
                "requests": 0
            }

        # Update stats
        self.usage[provider][model]["input_tokens"] += input_tokens
        self.usage[provider][model]["output_tokens"] += output_tokens
        self.usage[provider][model]["cost"] += cost
        self.usage[provider][model]["requests"] += 1
        self.total_cost += cost

    def get_summary(self) -> Dict:
        """Get usage summary"""
        return {
            "total_cost": self.total_cost,
            "by_provider": self.usage
        }

    def get_total_cost(self) -> float:
        """Get total cost in USD"""
        return self.total_cost

    def get_savings_vs_most_expensive(self) -> Tuple[float, str]:
        """Calculate savings by using cheaper models"""
        if not self.usage:
            return 0.0, ""

        # Find most expensive provider
        most_expensive_cost = 0.0
        most_expensive_name = ""

        for provider, models in self.usage.items():
            for model, stats in models.items():
                if stats["cost"] > most_expensive_cost:
                    most_expensive_cost = stats["cost"]
                    most_expensive_name = f"{provider}/{model}"

        if most_expensive_cost == 0:
            return 0.0, ""

        # Calculate what total would be if all requests used most expensive
        total_requests = sum(
            stats["requests"]
            for models in self.usage.values()
            for stats in models.values()
        )

        if total_requests == 0:
            return 0.0, ""

        avg_cost_most_expensive = most_expensive_cost / self.usage[most_expensive_name.split("/")[0]][most_expensive_name.split("/")[1]]["requests"]
        hypothetical_cost = avg_cost_most_expensive * total_requests
        savings = hypothetical_cost - self.total_cost

        return max(0, savings), most_expensive_name
