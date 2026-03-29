"""3-Layer Memory System for Bop Buddy
Implements short-term, medium-term, and long-term memory for conversations.

Memory Layers:
- Layer 1: Recent (24 hours) - Instant recall, highly detailed
- Layer 2: Weekly (7 days) - Important conversations and patterns
- Layer 3: Long-term (up to 1.5 years) - Key insights, preferences, important moments
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict


class MemoryLayer:
    """Base class for memory layers"""

    def __init__(self, name: str, retention_days: int):
        self.name = name
        self.retention_days = retention_days
        self.memories: List[Dict] = []

    def add_memory(self, memory: Dict):
        """Add a memory to this layer"""
        memory['layer'] = self.name
        memory['timestamp'] = datetime.now().isoformat()
        self.memories.append(memory)
        self._cleanup_old_memories()

    def _cleanup_old_memories(self):
        """Remove memories older than retention period"""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        self.memories = [
            m for m in self.memories
            if datetime.fromisoformat(m['timestamp']) > cutoff
        ]

    def get_memories(self, limit: Optional[int] = None) -> List[Dict]:
        """Get memories from this layer, most recent first"""
        self._cleanup_old_memories()
        sorted_memories = sorted(
            self.memories,
            key=lambda x: x['timestamp'],
            reverse=True
        )
        return sorted_memories[:limit] if limit else sorted_memories

    def search_memories(self, query: str) -> List[Dict]:
        """Search memories by content"""
        query_lower = query.lower()
        return [
            m for m in self.memories
            if query_lower in str(m.get('content', '')).lower()
            or query_lower in str(m.get('topic', '')).lower()
            or query_lower in str(m.get('tags', [])).lower()
        ]

    def count(self) -> int:
        """Count current memories in this layer"""
        self._cleanup_old_memories()
        return len(self.memories)


class ThreeLayerMemory:
    """Three-layer memory system for AI conversations

    Layer 1 (Recent): 24 hours - All conversations, highly detailed
    Layer 2 (Weekly): 7 days - Important patterns, topics, user preferences
    Layer 3 (Long-term): 540 days (~1.5 years) - Key insights, relationships, growth
    """

    def __init__(self, storage_dir: str = "memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        # Initialize memory layers
        self.recent = MemoryLayer("recent", retention_days=1)
        self.weekly = MemoryLayer("weekly", retention_days=7)
        self.longterm = MemoryLayer("longterm", retention_days=540)  # ~1.5 years

        # User profile and learning
        self.user_profile = {
            "preferences": {},
            "interests": [],
            "communication_style": {},
            "important_facts": [],
            "emotional_patterns": [],
            "goals": []
        }

        self._load_all_memories()

    def _get_storage_file(self, layer_name: str) -> Path:
        """Get storage file path for a layer"""
        return self.storage_dir / f"{layer_name}_memory.json"

    def _load_all_memories(self):
        """Load all memories from disk"""
        # Load each layer
        for layer in [self.recent, self.weekly, self.longterm]:
            storage_file = self._get_storage_file(layer.name)
            if storage_file.exists():
                try:
                    with open(storage_file, 'r') as f:
                        data = json.load(f)
                        layer.memories = data.get('memories', [])
                except Exception as e:
                    print(f"Error loading {layer.name} memories: {e}")

        # Load user profile
        profile_file = self.storage_dir / "user_profile.json"
        if profile_file.exists():
            try:
                with open(profile_file, 'r') as f:
                    self.user_profile = json.load(f)
            except Exception as e:
                print(f"Error loading user profile: {e}")

    def _save_all_memories(self):
        """Save all memories to disk"""
        # Save each layer
        for layer in [self.recent, self.weekly, self.longterm]:
            storage_file = self._get_storage_file(layer.name)
            try:
                with open(storage_file, 'w') as f:
                    json.dump({
                        'memories': layer.memories,
                        'last_updated': datetime.now().isoformat()
                    }, f, indent=2)
            except Exception as e:
                print(f"Error saving {layer.name} memories: {e}")

        # Save user profile
        profile_file = self.storage_dir / "user_profile.json"
        try:
            with open(profile_file, 'w') as f:
                json.dump(self.user_profile, f, indent=2)
        except Exception as e:
            print(f"Error saving user profile: {e}")

    def add_conversation(self, user_message: str, ai_response: str,
                        emotion: Optional[str] = None,
                        topics: Optional[List[str]] = None,
                        importance: int = 1):
        """Add a conversation to memory

        Args:
            user_message: What the user said
            ai_response: How the AI responded
            emotion: Detected emotion (happy, sad, excited, frustrated, etc.)
            topics: List of topics discussed
            importance: 1-5 scale, 5 being most important
        """
        memory = {
            "type": "conversation",
            "user_message": user_message,
            "ai_response": ai_response,
            "emotion": emotion,
            "topics": topics or [],
            "importance": importance,
            "timestamp": datetime.now().isoformat()
        }

        # Always add to recent memory (24 hours)
        self.recent.add_memory(memory.copy())

        # Add to weekly if importance >= 2
        if importance >= 2:
            self.weekly.add_memory(memory.copy())

        # Add to long-term if importance >= 4
        if importance >= 4:
            self.longterm.add_memory(memory.copy())

        # Extract and update user profile
        self._update_user_profile(memory)

        # Save to disk
        self._save_all_memories()

    def add_user_fact(self, fact: str, category: str = "general"):
        """Add an important fact about the user

        Examples:
        - "Prefers Python over JavaScript"
        - "Has a dog named Max"
        - "Works as a software engineer"
        - "Loves rock music"
        """
        fact_entry = {
            "fact": fact,
            "category": category,
            "learned_at": datetime.now().isoformat()
        }

        # Add to long-term memory
        self.longterm.add_memory({
            "type": "user_fact",
            "content": fact,
            "category": category
        })

        # Update user profile
        if fact_entry not in self.user_profile["important_facts"]:
            self.user_profile["important_facts"].append(fact_entry)

        self._save_all_memories()

    def add_preference(self, preference_key: str, preference_value: Any):
        """Add or update a user preference

        Examples:
        - ("communication_style", "casual")
        - ("code_language", "python")
        - ("response_length", "concise")
        """
        self.user_profile["preferences"][preference_key] = {
            "value": preference_value,
            "updated_at": datetime.now().isoformat()
        }
        self._save_all_memories()

    def add_goal(self, goal: str, deadline: Optional[str] = None):
        """Add a user goal to track

        Examples:
        - "Build a mobile app"
        - "Learn machine learning"
        - "Launch a startup"
        """
        goal_entry = {
            "goal": goal,
            "added_at": datetime.now().isoformat(),
            "deadline": deadline,
            "completed": False
        }

        self.user_profile["goals"].append(goal_entry)

        # Add to long-term memory
        self.longterm.add_memory({
            "type": "goal",
            "content": goal,
            "deadline": deadline
        })

        self._save_all_memories()

    def _update_user_profile(self, memory: Dict):
        """Extract insights from conversation and update user profile"""
        topics = memory.get("topics", [])
        emotion = memory.get("emotion")

        # Track interests based on topics
        for topic in topics:
            if topic not in self.user_profile["interests"]:
                self.user_profile["interests"].append(topic)

        # Track emotional patterns
        if emotion:
            emotion_entry = {
                "emotion": emotion,
                "timestamp": memory["timestamp"],
                "context": memory.get("user_message", "")[:100]
            }
            self.user_profile["emotional_patterns"].append(emotion_entry)

            # Keep only last 50 emotional patterns
            self.user_profile["emotional_patterns"] = \
                self.user_profile["emotional_patterns"][-50:]

    def get_context_for_conversation(self, query: Optional[str] = None,
                                    max_recent: int = 5,
                                    max_weekly: int = 3,
                                    max_longterm: int = 2) -> str:
        """Get relevant context from all memory layers

        Returns a formatted string with relevant memories to provide context
        for the AI's next response.
        """
        context_parts = []

        # Recent memory (last 24 hours)
        recent_memories = self.recent.get_memories(limit=max_recent)
        if recent_memories:
            context_parts.append("## Recent Memory (Last 24 Hours)")
            for mem in recent_memories:
                if mem.get("type") == "conversation":
                    context_parts.append(f"- User: {mem.get('user_message', '')[:100]}...")
                    if mem.get("emotion"):
                        context_parts.append(f"  Emotion: {mem['emotion']}")

        # Weekly memory (important from last 7 days)
        weekly_memories = self.weekly.get_memories(limit=max_weekly)
        if weekly_memories:
            context_parts.append("\n## This Week's Important Conversations")
            for mem in weekly_memories:
                topics = mem.get("topics", [])
                topic_str = ", ".join(topics) if topics else "General"
                context_parts.append(f"- [{topic_str}] {mem.get('user_message', '')[:80]}...")

        # Long-term memory (key facts and patterns)
        context_parts.append("\n## Long-term Knowledge About User")

        # User facts
        if self.user_profile["important_facts"]:
            context_parts.append("### Important Facts:")
            for fact in self.user_profile["important_facts"][-5:]:
                context_parts.append(f"- {fact['fact']}")

        # Preferences
        if self.user_profile["preferences"]:
            context_parts.append("### Preferences:")
            for key, data in list(self.user_profile["preferences"].items())[:5]:
                context_parts.append(f"- {key}: {data['value']}")

        # Interests
        if self.user_profile["interests"]:
            context_parts.append(f"### Interests: {', '.join(self.user_profile['interests'][-10:])}")

        # Active goals
        active_goals = [g for g in self.user_profile["goals"] if not g.get("completed")]
        if active_goals:
            context_parts.append("### Active Goals:")
            for goal in active_goals[-3:]:
                deadline = f" (by {goal['deadline']})" if goal.get('deadline') else ""
                context_parts.append(f"- {goal['goal']}{deadline}")

        # Query-specific search
        if query:
            search_results = self.search_all_layers(query, limit=2)
            if search_results:
                context_parts.append(f"\n## Relevant to '{query}':")
                for result in search_results:
                    context_parts.append(f"- [{result['layer']}] {result.get('user_message', result.get('content', ''))[:80]}...")

        return "\n".join(context_parts)

    def search_all_layers(self, query: str, limit: Optional[int] = None) -> List[Dict]:
        """Search across all memory layers"""
        results = []

        for layer in [self.recent, self.weekly, self.longterm]:
            layer_results = layer.search_memories(query)
            results.extend(layer_results)

        # Sort by timestamp, most recent first
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return results[:limit] if limit else results

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage"""
        return {
            "recent_count": self.recent.count(),
            "weekly_count": self.weekly.count(),
            "longterm_count": self.longterm.count(),
            "total_facts": len(self.user_profile["important_facts"]),
            "total_preferences": len(self.user_profile["preferences"]),
            "total_interests": len(self.user_profile["interests"]),
            "active_goals": len([g for g in self.user_profile["goals"] if not g.get("completed")]),
            "emotional_patterns_tracked": len(self.user_profile["emotional_patterns"])
        }

    def get_user_summary(self) -> str:
        """Get a summary of what the AI knows about the user"""
        summary_parts = [
            "# User Profile Summary",
            f"\n**Total Conversations Stored**: {self.recent.count() + self.weekly.count() + self.longterm.count()}",
        ]

        if self.user_profile["important_facts"]:
            summary_parts.append("\n## Key Facts:")
            for fact in self.user_profile["important_facts"]:
                summary_parts.append(f"- {fact['fact']} (learned {fact['learned_at'][:10]})")

        if self.user_profile["preferences"]:
            summary_parts.append("\n## Preferences:")
            for key, data in self.user_profile["preferences"].items():
                summary_parts.append(f"- {key}: {data['value']}")

        if self.user_profile["interests"]:
            summary_parts.append(f"\n## Interests:\n{', '.join(self.user_profile['interests'])}")

        if self.user_profile["goals"]:
            summary_parts.append("\n## Goals:")
            for goal in self.user_profile["goals"]:
                status = "✓" if goal.get("completed") else "○"
                summary_parts.append(f"{status} {goal['goal']}")

        return "\n".join(summary_parts)

    def clear_layer(self, layer_name: str):
        """Clear a specific memory layer"""
        if layer_name == "recent":
            self.recent.memories = []
        elif layer_name == "weekly":
            self.weekly.memories = []
        elif layer_name == "longterm":
            self.longterm.memories = []

        self._save_all_memories()

    def clear_all(self):
        """Clear all memories (use with caution!)"""
        self.recent.memories = []
        self.weekly.memories = []
        self.longterm.memories = []
        self.user_profile = {
            "preferences": {},
            "interests": [],
            "communication_style": {},
            "important_facts": [],
            "emotional_patterns": [],
            "goals": []
        }
        self._save_all_memories()

    def export_memories(self) -> Dict[str, Any]:
        """Export all memories for backup or transfer"""
        return {
            "recent": self.recent.memories,
            "weekly": self.weekly.memories,
            "longterm": self.longterm.memories,
            "user_profile": self.user_profile,
            "exported_at": datetime.now().isoformat()
        }

    def import_memories(self, data: Dict[str, Any]):
        """Import memories from backup"""
        self.recent.memories = data.get("recent", [])
        self.weekly.memories = data.get("weekly", [])
        self.longterm.memories = data.get("longterm", [])
        self.user_profile = data.get("user_profile", self.user_profile)
        self._save_all_memories()
