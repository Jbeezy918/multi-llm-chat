"""Subscription & Tier Management - Premium Revenue Engine"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum


class SubscriptionTier(Enum):
    """Subscription tier levels"""
    FREE = "free"
    PREMIUM = "premium"
    TEAM = "team"
    PRO = "pro"


# Tier definitions with pricing and features
SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "billing": "forever",
        "features": {
            "conversations_per_day": 10,
            "models_per_query": 4,
            "cost_analytics": False,
            "referral_rewards": False,
            "priority_support": False,
            "shared_workspace": False,
            "team_size": 1,
            "conversation_export": False,
            "api_access": False,
            "white_label": False,
            "advanced_settings": False
        },
        "description": "Perfect for trying out multi-LLM comparison",
        "cta": "Get Started Free"
    },
    "premium": {
        "name": "Premium",
        "price": 8.99,
        "billing": "per month",
        "features": {
            "conversations_per_day": -1,  # unlimited
            "models_per_query": 4,
            "cost_analytics": True,
            "referral_rewards": True,
            "priority_support": True,
            "shared_workspace": False,
            "team_size": 1,
            "conversation_export": True,
            "api_access": False,
            "white_label": False,
            "advanced_settings": True
        },
        "description": "Unlimited queries + full analytics + referral rewards",
        "cta": "Upgrade to Premium"
    },
    "team": {
        "name": "Team",
        "price": 29.99,
        "billing": "per month",
        "features": {
            "conversations_per_day": -1,  # unlimited
            "models_per_query": 4,
            "cost_analytics": True,
            "referral_rewards": True,
            "priority_support": True,
            "shared_workspace": True,
            "team_size": 5,
            "conversation_export": True,
            "api_access": False,
            "white_label": False,
            "advanced_settings": True
        },
        "description": "Premium features + 5 team members + shared workspace",
        "cta": "Upgrade to Team"
    },
    "pro": {
        "name": "Pro/API",
        "price": 49.99,
        "billing": "per month",
        "features": {
            "conversations_per_day": -1,  # unlimited
            "models_per_query": 4,
            "cost_analytics": True,
            "referral_rewards": True,
            "priority_support": True,
            "shared_workspace": True,
            "team_size": -1,  # unlimited
            "conversation_export": True,
            "api_access": True,
            "white_label": True,
            "advanced_settings": True
        },
        "description": "Everything + API access + white-label option",
        "cta": "Upgrade to Pro"
    }
}


class SubscriptionManager:
    """Manage subscription tiers, upgrades, and feature access"""

    def __init__(self, analytics_dir: str = "analytics"):
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(exist_ok=True)
        self.subscriptions_file = self.analytics_dir / "subscriptions.json"
        self.subscriptions = self._load_subscriptions()

    def _load_subscriptions(self) -> Dict:
        """Load subscriptions from file"""
        if self.subscriptions_file.exists():
            with open(self.subscriptions_file, 'r') as f:
                return json.load(f)
        return {
            "users": {},  # {email: {tier, started_at, usage_stats, team_members, etc}}
            "events": []  # [{timestamp, email, event_type, metadata}]
        }

    def _save_subscriptions(self):
        """Save subscriptions to file"""
        with open(self.subscriptions_file, 'w') as f:
            json.dump(self.subscriptions, f, indent=2)

    def create_subscription(self, email: str, tier: str = "free", name: Optional[str] = None) -> Dict:
        """Create new subscription for user"""
        if tier not in SUBSCRIPTION_TIERS:
            tier = "free"

        if email not in self.subscriptions["users"]:
            self.subscriptions["users"][email] = {
                "email": email,
                "name": name,
                "tier": tier,
                "started_at": datetime.now().isoformat(),
                "tier_started_at": datetime.now().isoformat(),
                "usage_stats": {
                    "conversations_today": 0,
                    "last_reset": datetime.now().date().isoformat(),
                    "total_conversations": 0,
                    "total_queries": 0
                },
                "team_members": [],
                "is_active": True,
                "billing_cycle_start": datetime.now().isoformat(),
                "next_billing_date": (datetime.now() + timedelta(days=30)).isoformat() if tier != "free" else None
            }

            # Track event
            self._track_event(email, "subscription_created", {"tier": tier})
            self._save_subscriptions()

        return self.subscriptions["users"][email]

    def get_subscription(self, email: str) -> Optional[Dict]:
        """Get subscription for user"""
        return self.subscriptions["users"].get(email)

    def upgrade_subscription(self, email: str, new_tier: str) -> bool:
        """Upgrade user to higher tier"""
        if email not in self.subscriptions["users"]:
            return False

        if new_tier not in SUBSCRIPTION_TIERS:
            return False

        old_tier = self.subscriptions["users"][email]["tier"]

        # Update tier
        self.subscriptions["users"][email]["tier"] = new_tier
        self.subscriptions["users"][email]["tier_started_at"] = datetime.now().isoformat()
        self.subscriptions["users"][email]["billing_cycle_start"] = datetime.now().isoformat()
        self.subscriptions["users"][email]["next_billing_date"] = (
            datetime.now() + timedelta(days=30)
        ).isoformat()

        # Track event
        self._track_event(email, "subscription_upgraded", {
            "old_tier": old_tier,
            "new_tier": new_tier
        })

        self._save_subscriptions()
        return True

    def downgrade_subscription(self, email: str, new_tier: str) -> bool:
        """Downgrade user to lower tier"""
        if email not in self.subscriptions["users"]:
            return False

        if new_tier not in SUBSCRIPTION_TIERS:
            return False

        old_tier = self.subscriptions["users"][email]["tier"]

        # Update tier
        self.subscriptions["users"][email]["tier"] = new_tier
        self.subscriptions["users"][email]["tier_started_at"] = datetime.now().isoformat()

        # If downgrading to free, clear billing dates
        if new_tier == "free":
            self.subscriptions["users"][email]["next_billing_date"] = None

        # Track event
        self._track_event(email, "subscription_downgraded", {
            "old_tier": old_tier,
            "new_tier": new_tier
        })

        self._save_subscriptions()
        return True

    def check_feature_access(self, email: str, feature: str) -> bool:
        """Check if user has access to a feature"""
        subscription = self.get_subscription(email)

        if not subscription:
            # No subscription = free tier
            return SUBSCRIPTION_TIERS["free"]["features"].get(feature, False)

        tier = subscription["tier"]
        tier_features = SUBSCRIPTION_TIERS[tier]["features"]

        return tier_features.get(feature, False)

    def get_feature_limit(self, email: str, feature: str) -> int:
        """Get numeric limit for a feature (-1 = unlimited)"""
        subscription = self.get_subscription(email)

        if not subscription:
            tier = "free"
        else:
            tier = subscription["tier"]

        tier_features = SUBSCRIPTION_TIERS[tier]["features"]
        return tier_features.get(feature, 0)

    def track_usage(self, email: str, usage_type: str = "conversation"):
        """Track usage for rate limiting"""
        subscription = self.get_subscription(email)

        if not subscription:
            # Create free tier subscription
            self.create_subscription(email)
            subscription = self.get_subscription(email)

        # Reset daily counter if new day
        today = datetime.now().date().isoformat()
        if subscription["usage_stats"]["last_reset"] != today:
            subscription["usage_stats"]["conversations_today"] = 0
            subscription["usage_stats"]["last_reset"] = today

        # Increment counters
        if usage_type == "conversation":
            subscription["usage_stats"]["conversations_today"] += 1
            subscription["usage_stats"]["total_conversations"] += 1
        elif usage_type == "query":
            subscription["usage_stats"]["total_queries"] += 1

        self._save_subscriptions()

    def check_usage_limit(self, email: str) -> Dict:
        """Check if user has hit usage limit"""
        subscription = self.get_subscription(email)

        if not subscription:
            # No subscription = free tier limits
            return {
                "allowed": True,
                "limit": SUBSCRIPTION_TIERS["free"]["features"]["conversations_per_day"],
                "used": 0,
                "remaining": SUBSCRIPTION_TIERS["free"]["features"]["conversations_per_day"]
            }

        tier = subscription["tier"]
        limit = SUBSCRIPTION_TIERS[tier]["features"]["conversations_per_day"]

        # -1 means unlimited
        if limit == -1:
            return {
                "allowed": True,
                "limit": -1,
                "used": subscription["usage_stats"]["conversations_today"],
                "remaining": -1
            }

        # Reset if new day
        today = datetime.now().date().isoformat()
        if subscription["usage_stats"]["last_reset"] != today:
            subscription["usage_stats"]["conversations_today"] = 0
            subscription["usage_stats"]["last_reset"] = today
            self._save_subscriptions()

        used = subscription["usage_stats"]["conversations_today"]
        remaining = max(0, limit - used)

        return {
            "allowed": used < limit,
            "limit": limit,
            "used": used,
            "remaining": remaining
        }

    def get_tier_info(self, tier: str) -> Dict:
        """Get tier information"""
        return SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["free"])

    def get_all_tiers(self) -> Dict:
        """Get all tier information"""
        return SUBSCRIPTION_TIERS

    def get_upgrade_cta(self, email: str, context: str = "general") -> Optional[Dict]:
        """Get contextual upgrade CTA"""
        subscription = self.get_subscription(email)

        if not subscription or subscription["tier"] == "free":
            # Free user - suggest Premium
            ctas = {
                "cost_analytics": {
                    "headline": "Want detailed cost analytics?",
                    "description": "Track your AI spending with Premium",
                    "target_tier": "premium",
                    "cta_text": "Upgrade to Premium - $8.99/mo"
                },
                "referral_rewards": {
                    "headline": "Unlock referral rewards",
                    "description": "Earn up to 30 days free with Premium",
                    "target_tier": "premium",
                    "cta_text": "Upgrade to Premium - $8.99/mo"
                },
                "usage_limit": {
                    "headline": "Hit your daily limit?",
                    "description": "Get unlimited conversations with Premium",
                    "target_tier": "premium",
                    "cta_text": "Upgrade to Premium - $8.99/mo"
                },
                "general": {
                    "headline": "Ready for more?",
                    "description": "Unlimited queries + cost analytics + priority support",
                    "target_tier": "premium",
                    "cta_text": "Upgrade to Premium - $8.99/mo"
                }
            }
            return ctas.get(context, ctas["general"])

        elif subscription["tier"] == "premium":
            # Premium user - suggest Team
            return {
                "headline": "Working with a team?",
                "description": "Share workspace with up to 5 team members",
                "target_tier": "team",
                "cta_text": "Upgrade to Team - $29.99/mo"
            }

        elif subscription["tier"] == "team":
            # Team user - suggest Pro
            return {
                "headline": "Need API access?",
                "description": "Get API access + white-label options",
                "target_tier": "pro",
                "cta_text": "Upgrade to Pro - $49.99/mo"
            }

        # Pro user - no upgrade needed
        return None

    def _track_event(self, email: str, event_type: str, metadata: Optional[Dict] = None):
        """Track subscription event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "email": email,
            "event_type": event_type,
            "metadata": metadata or {}
        }

        self.subscriptions["events"].append(event)

    def get_subscription_stats(self) -> Dict:
        """Get overall subscription statistics"""
        total_users = len(self.subscriptions["users"])
        tier_counts = {"free": 0, "premium": 0, "team": 0, "pro": 0}

        for user_data in self.subscriptions["users"].values():
            tier = user_data["tier"]
            tier_counts[tier] += 1

        # Calculate MRR
        mrr = (
            tier_counts["premium"] * SUBSCRIPTION_TIERS["premium"]["price"] +
            tier_counts["team"] * SUBSCRIPTION_TIERS["team"]["price"] +
            tier_counts["pro"] * SUBSCRIPTION_TIERS["pro"]["price"]
        )

        return {
            "total_users": total_users,
            "tier_distribution": tier_counts,
            "mrr": round(mrr, 2),
            "conversion_rate": (
                (tier_counts["premium"] + tier_counts["team"] + tier_counts["pro"]) / total_users * 100
                if total_users > 0 else 0
            )
        }


def get_pricing_table() -> List[Dict]:
    """Get pricing table for display"""
    tiers = []
    for tier_id, tier_data in SUBSCRIPTION_TIERS.items():
        tiers.append({
            "id": tier_id,
            "name": tier_data["name"],
            "price": tier_data["price"],
            "billing": tier_data["billing"],
            "description": tier_data["description"],
            "cta": tier_data["cta"],
            "features": tier_data["features"]
        })
    return tiers


def format_tier_features(tier: str) -> List[str]:
    """Format tier features for display"""
    if tier not in SUBSCRIPTION_TIERS:
        tier = "free"

    features = SUBSCRIPTION_TIERS[tier]["features"]
    formatted = []

    # Conversations
    if features["conversations_per_day"] == -1:
        formatted.append("✅ Unlimited conversations")
    else:
        formatted.append(f"✅ {features['conversations_per_day']} conversations/day")

    # Cost analytics
    if features["cost_analytics"]:
        formatted.append("✅ Detailed cost analytics")

    # Referral rewards
    if features["referral_rewards"]:
        formatted.append("✅ Referral rewards program")

    # Priority support
    if features["priority_support"]:
        formatted.append("✅ Priority support")

    # Shared workspace
    if features["shared_workspace"]:
        if features["team_size"] == -1:
            formatted.append("✅ Unlimited team members")
        else:
            formatted.append(f"✅ Team workspace (up to {features['team_size']} members)")

    # Conversation export
    if features["conversation_export"]:
        formatted.append("✅ Export conversations")

    # API access
    if features["api_access"]:
        formatted.append("✅ API access")

    # White label
    if features["white_label"]:
        formatted.append("✅ White-label option")

    # Advanced settings
    if features["advanced_settings"]:
        formatted.append("✅ Advanced model settings")

    return formatted
