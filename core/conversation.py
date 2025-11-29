"""Conversation History Management"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class ConversationManager:
    """Manage conversation history with persistence"""

    def __init__(self, storage_dir: str = "conversations"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.current_conversation: List[Dict[str, Any]] = []

    def add_message(self, prompt: str, responses: Dict[str, str]):
        """Add a new message exchange to conversation"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "responses": responses
        }
        self.current_conversation.append(entry)

    def get_history(self) -> List[Dict[str, Any]]:
        """Get current conversation history"""
        return self.current_conversation

    def clear_history(self):
        """Clear current conversation"""
        self.current_conversation = []

    def save_conversation(self, name: Optional[str] = None) -> str:
        """Save conversation to file"""
        if not self.current_conversation:
            return "No conversation to save"

        if not name:
            name = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        filepath = self.storage_dir / f"{name}.json"

        with open(filepath, 'w') as f:
            json.dump(self.current_conversation, f, indent=2)

        return str(filepath)

    def load_conversation(self, filepath: str) -> bool:
        """Load conversation from file"""
        try:
            with open(filepath, 'r') as f:
                self.current_conversation = json.load(f)
            return True
        except Exception as e:
            print(f"Failed to load conversation: {e}")
            return False

    def list_saved_conversations(self) -> List[str]:
        """List all saved conversations"""
        if not self.storage_dir.exists():
            return []
        return [str(f) for f in self.storage_dir.glob("*.json")]

    def export_markdown(self) -> str:
        """Export conversation as markdown"""
        md = "# Multi-LLM Conversation\n\n"
        md += f"**Exported**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        md += "---\n\n"

        for i, entry in enumerate(self.current_conversation, 1):
            md += f"## Exchange {i}\n\n"
            md += f"**Time**: {entry['timestamp']}\n\n"
            md += f"**Prompt**: {entry['prompt']}\n\n"

            for provider, response in entry['responses'].items():
                md += f"### {provider}\n\n"
                md += f"{response}\n\n"

            md += "---\n\n"

        return md

    def export_json(self) -> str:
        """Export conversation as JSON string"""
        return json.dumps(self.current_conversation, indent=2)
