"""Referral System - Viral Growth Engine"""
import json
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


def generate_referral_code(email: str) -> str:
    """Generate unique referral code from email"""
    # Create deterministic but unique code from email
    hash_obj = hashlib.sha256(email.encode())
    # Take first 8 characters of hash
    code = hash_obj.hexdigest()[:8].upper()
    return code


def generate_shareable_link(base_url: str, referral_code: str) -> str:
    """Generate shareable referral link"""
    return f"{base_url}?ref={referral_code}"


class ReferralManager:
    """Manage referral codes, tracking, and rewards"""

    def __init__(self, analytics_dir: str = "analytics"):
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(exist_ok=True)
        self.referrals_file = self.analytics_dir / "referrals.json"
        self.referrals = self._load_referrals()

    def _load_referrals(self) -> Dict:
        """Load referrals from file"""
        if self.referrals_file.exists():
            with open(self.referrals_file, 'r') as f:
                return json.load(f)
        return {
            "codes": {},  # {code: {email, created_at, referrals: []}}
            "events": []  # [{timestamp, code, event_type, metadata}]
        }

    def _save_referrals(self):
        """Save referrals to file"""
        with open(self.referrals_file, 'w') as f:
            json.dump(self.referrals, f, indent=2)

    def create_referral_code(self, email: str, name: Optional[str] = None) -> str:
        """Create referral code for user"""
        code = generate_referral_code(email)

        if code not in self.referrals["codes"]:
            self.referrals["codes"][code] = {
                "email": email,
                "name": name,
                "created_at": datetime.now().isoformat(),
                "referrals": [],
                "conversions": 0,
                "premium_conversions": 0,
                "rewards_earned": 0
            }
            self._save_referrals()

        return code

    def track_referral_visit(self, referral_code: str, visitor_metadata: Optional[Dict] = None):
        """Track when someone visits via referral link"""
        if referral_code not in self.referrals["codes"]:
            return False

        event = {
            "timestamp": datetime.now().isoformat(),
            "code": referral_code,
            "event_type": "visit",
            "metadata": visitor_metadata or {}
        }

        self.referrals["events"].append(event)
        self._save_referrals()
        return True

    def track_referral_signup(self, referral_code: str, new_email: str, new_name: Optional[str] = None):
        """Track when referred user signs up (captures email)"""
        if referral_code not in self.referrals["codes"]:
            return False

        # Add to referrals list
        self.referrals["codes"][referral_code]["referrals"].append({
            "email": new_email,
            "name": new_name,
            "signed_up_at": datetime.now().isoformat(),
            "converted_to_premium": False
        })

        # Track event
        event = {
            "timestamp": datetime.now().isoformat(),
            "code": referral_code,
            "event_type": "signup",
            "metadata": {"email": new_email, "name": new_name}
        }

        self.referrals["events"].append(event)
        self.referrals["codes"][referral_code]["conversions"] += 1

        # Award reward (1 week free = 7 days)
        self.referrals["codes"][referral_code]["rewards_earned"] += 7

        self._save_referrals()
        return True

    def track_referral_premium(self, referral_code: str, converted_email: str):
        """Track when referred user upgrades to premium"""
        if referral_code not in self.referrals["codes"]:
            return False

        # Update referral to mark as premium
        for referral in self.referrals["codes"][referral_code]["referrals"]:
            if referral["email"] == converted_email:
                referral["converted_to_premium"] = True
                referral["premium_at"] = datetime.now().isoformat()

        # Track event
        event = {
            "timestamp": datetime.now().isoformat(),
            "code": referral_code,
            "event_type": "premium_conversion",
            "metadata": {"email": converted_email}
        }

        self.referrals["events"].append(event)
        self.referrals["codes"][referral_code]["premium_conversions"] += 1

        # Bonus reward for premium conversion (1 month free)
        self.referrals["codes"][referral_code]["rewards_earned"] += 30

        self._save_referrals()
        return True

    def get_referral_stats(self, referral_code: str) -> Optional[Dict]:
        """Get stats for a referral code"""
        if referral_code not in self.referrals["codes"]:
            return None

        code_data = self.referrals["codes"][referral_code]

        return {
            "total_visits": len([e for e in self.referrals["events"] if e["code"] == referral_code and e["event_type"] == "visit"]),
            "total_signups": code_data["conversions"],
            "premium_conversions": code_data["premium_conversions"],
            "rewards_earned_days": code_data["rewards_earned"],
            "referrals": code_data["referrals"]
        }

    def get_all_referral_stats(self) -> Dict:
        """Get overall referral system stats"""
        total_codes = len(self.referrals["codes"])
        total_visits = len([e for e in self.referrals["events"] if e["event_type"] == "visit"])
        total_signups = sum(c["conversions"] for c in self.referrals["codes"].values())
        total_premium = sum(c["premium_conversions"] for c in self.referrals["codes"].values())

        return {
            "total_referral_codes": total_codes,
            "total_visits": total_visits,
            "total_signups": total_signups,
            "total_premium_conversions": total_premium,
            "conversion_rate": (total_signups / total_visits * 100) if total_visits > 0 else 0,
            "premium_conversion_rate": (total_premium / total_signups * 100) if total_signups > 0 else 0
        }

    def get_top_referrers(self, limit: int = 10) -> List[Dict]:
        """Get top referrers by conversions"""
        referrers = []

        for code, data in self.referrals["codes"].items():
            referrers.append({
                "code": code,
                "email": data["email"],
                "name": data.get("name"),
                "conversions": data["conversions"],
                "premium_conversions": data["premium_conversions"],
                "rewards_earned": data["rewards_earned"]
            })

        # Sort by conversions
        referrers.sort(key=lambda x: (x["premium_conversions"], x["conversions"]), reverse=True)

        return referrers[:limit]
