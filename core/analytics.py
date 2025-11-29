"""Usage Analytics & Email Capture - Monetization Focused"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class UsageLogger:
    """Log usage for analytics and follow-up"""

    def __init__(self, log_dir: str = "analytics"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.session_file = self.log_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.email_file = self.log_dir / "emails.json"
        self.session_data = {
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "user_email": None,
            "user_name": None
        }

    def log_interaction(
        self,
        prompt: str,
        providers_used: list,
        tokens_used: Dict[str, int],
        cost: float
    ):
        """Log a single interaction"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "prompt_preview": prompt[:100],  # Privacy: only store preview
            "prompt_length": len(prompt),
            "providers_used": providers_used,
            "tokens_used": tokens_used,
            "cost": cost
        }
        self.session_data["interactions"].append(interaction)
        self._save_session()

    def capture_email(self, email: str, name: Optional[str] = None):
        """Capture user email for follow-up"""
        self.session_data["user_email"] = email
        self.session_data["user_name"] = name
        self._save_session()
        self._save_email(email, name)

    def _save_session(self):
        """Save session data to file"""
        with open(self.session_file, 'w') as f:
            json.dump(self.session_data, f, indent=2)

    def _save_email(self, email: str, name: Optional[str]):
        """Save email to master list"""
        emails = []
        if self.email_file.exists():
            with open(self.email_file, 'r') as f:
                emails = json.load(f)

        # Check if email already exists
        if not any(e["email"] == email for e in emails):
            emails.append({
                "email": email,
                "name": name,
                "captured_at": datetime.now().isoformat(),
                "first_session": str(self.session_file)
            })

            with open(self.email_file, 'w') as f:
                json.dump(emails, f, indent=2)

    def get_session_stats(self) -> Dict[str, Any]:
        """Get stats for current session"""
        if not self.session_data["interactions"]:
            return {
                "total_interactions": 0,
                "total_cost": 0.0,
                "providers_used": [],
                "session_duration": "0m"
            }

        total_cost = sum(i["cost"] for i in self.session_data["interactions"])
        providers = set()
        for interaction in self.session_data["interactions"]:
            providers.update(interaction["providers_used"])

        start = datetime.fromisoformat(self.session_data["start_time"])
        duration = datetime.now() - start
        duration_str = f"{int(duration.total_seconds() / 60)}m"

        return {
            "total_interactions": len(self.session_data["interactions"]),
            "total_cost": total_cost,
            "providers_used": list(providers),
            "session_duration": duration_str,
            "has_email": bool(self.session_data["user_email"])
        }


def get_total_users() -> int:
    """Get total number of users who've provided emails"""
    email_file = Path("analytics/emails.json")
    if not email_file.exists():
        return 0

    with open(email_file, 'r') as f:
        emails = json.load(f)
    return len(emails)


def get_total_sessions() -> int:
    """Get total number of sessions"""
    log_dir = Path("analytics")
    if not log_dir.exists():
        return 0
    return len(list(log_dir.glob("session_*.json")))
