"""Affiliate Link Management - Revenue Optimization"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


# Affiliate links for API providers
AFFILIATE_LINKS = {
    "openai": {
        "signup": "https://platform.openai.com/signup",  # Replace with affiliate link when available
        "docs": "https://platform.openai.com/docs",
        "pricing": "https://openai.com/pricing",
        "display_name": "OpenAI"
    },
    "anthropic": {
        "signup": "https://console.anthropic.com/signup",  # Replace with affiliate link
        "docs": "https://docs.anthropic.com",
        "pricing": "https://www.anthropic.com/api",
        "display_name": "Anthropic (Claude)"
    },
    "google": {
        "signup": "https://aistudio.google.com/app/apikey",  # Replace with affiliate link
        "docs": "https://ai.google.dev/docs",
        "pricing": "https://ai.google.dev/pricing",
        "display_name": "Google (Gemini)"
    },
    "ollama": {
        "signup": "https://ollama.com/download",
        "docs": "https://github.com/ollama/ollama",
        "pricing": "https://ollama.com",  # Free!
        "display_name": "Ollama (Free Local)"
    }
}


class AffiliateManager:
    """Manage affiliate links and track clicks"""

    def __init__(self, analytics_dir: str = "analytics"):
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(exist_ok=True)
        self.clicks_file = self.analytics_dir / "affiliate_clicks.json"
        self.clicks = self._load_clicks()

    def _load_clicks(self) -> list:
        """Load click data from file"""
        if self.clicks_file.exists():
            with open(self.clicks_file, 'r') as f:
                return json.load(f)
        return []

    def _save_clicks(self):
        """Save click data to file"""
        with open(self.clicks_file, 'w') as f:
            json.dump(self.clicks, f, indent=2)

    def get_affiliate_link(self, provider: str, link_type: str = "signup") -> Optional[str]:
        """Get affiliate link for provider"""
        provider = provider.lower()
        if provider in AFFILIATE_LINKS and link_type in AFFILIATE_LINKS[provider]:
            return AFFILIATE_LINKS[provider][link_type]
        return None

    def track_click(self, provider: str, link_type: str, user_metadata: Optional[Dict] = None):
        """Track affiliate link click"""
        click = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "link_type": link_type,
            "metadata": user_metadata or {}
        }

        self.clicks.append(click)
        self._save_clicks()

    def get_click_stats(self) -> Dict:
        """Get affiliate click statistics"""
        stats = {
            "total_clicks": len(self.clicks),
            "by_provider": {},
            "by_link_type": {}
        }

        for click in self.clicks:
            provider = click["provider"]
            link_type = click["link_type"]

            # Count by provider
            if provider not in stats["by_provider"]:
                stats["by_provider"][provider] = 0
            stats["by_provider"][provider] += 1

            # Count by link type
            if link_type not in stats["by_link_type"]:
                stats["by_link_type"][link_type] = 0
            stats["by_link_type"][link_type] += 1

        return stats

    def get_provider_cta(self, provider: str) -> Dict:
        """Get CTA copy for provider affiliate link"""
        provider = provider.lower()

        ctas = {
            "openai": {
                "headline": "Don't have an OpenAI API key?",
                "description": "Get started with $5 free credit",
                "cta_text": "Sign up for OpenAI →",
                "benefit": "Start with GPT-4o-mini at $0.15/1M tokens"
            },
            "anthropic": {
                "headline": "Want to try Claude?",
                "description": "Get started with Anthropic's API",
                "cta_text": "Sign up for Claude →",
                "benefit": "Best for reasoning and analysis"
            },
            "google": {
                "headline": "Try Gemini for free",
                "description": "Google's Gemini 2.0 Flash is free during preview",
                "cta_text": "Get Gemini API Key →",
                "benefit": "Free tier with generous limits"
            },
            "ollama": {
                "headline": "Use AI for $0/month",
                "description": "Run models locally with Ollama",
                "cta_text": "Download Ollama (Free) →",
                "benefit": "100% free, 100% private, runs offline"
            }
        }

        return ctas.get(provider, {})


def get_landing_page_affiliate_section() -> Dict[str, str]:
    """Get affiliate section for landing page"""
    return {
        "headline": "Get Started with AI Models",
        "subheadline": "Choose your provider and start comparing",
        "providers": AFFILIATE_LINKS
    }


def get_email_modal_affiliate_copy() -> str:
    """Get affiliate copy for email capture modal"""
    return """
    **Plus get our free guides:**
    - How to get $5-20 free credits from each AI provider
    - Which API to choose for your use case
    - Cost optimization secrets
    """
