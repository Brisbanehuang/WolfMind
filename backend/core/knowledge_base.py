# -*- coding: utf-8 -*-
"""Lightweight per-player knowledge checkpoint management."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict


class PlayerKnowledgeStore:
    """Manage long-lived game understanding for each player.

    A fresh, uniquely named checkpoint file is created on each program start
    to ensure the first game of a run always begins with an empty knowledge
    base. Knowledge is stored per player and is intentionally limited to
    long-term understanding/experience (no per-game speeches or votes).
    """

    def __init__(self, checkpoint_dir: str, base_filename: str) -> None:
        self.dir_path = Path(checkpoint_dir)
        self.dir_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"{base_filename}_{timestamp}"
        self.file_path = self.dir_path / f"{self.session_id}.json"

        # Keep everything in memory and mirror to disk on save.
        self._data: Dict[str, object] = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "players": {},
        }
        # Create the empty, unique file for this run.
        self.save()

    def load(self) -> Dict[str, object]:
        """Load knowledge from disk (if the file already has content)."""
        if self.file_path.exists():
            raw = self.file_path.read_text(encoding="utf-8")
            if raw.strip():
                try:
                    self._data = json.loads(raw)
                except json.JSONDecodeError:
                    # Keep current in-memory data if file is somehow broken.
                    pass
        return self._data

    def get_player_knowledge(self, name: str) -> str:
        """Return stored knowledge for a player (empty string if none)."""
        players = self._data.get("players", {}) if isinstance(
            self._data, dict) else {}
        return str(players.get(name, "")) if isinstance(players, dict) else ""

    def update_player_knowledge(self, name: str, knowledge: str) -> None:
        """Update the knowledge text for a player (in-memory only)."""
        if not isinstance(self._data, dict):
            self._data = {"session_id": self.session_id, "players": {}}
        players = self._data.setdefault(
            "players", {})  # type: ignore[arg-type]
        if isinstance(players, dict):
            players[name] = knowledge or ""

    def bulk_update(self, knowledge_map: Dict[str, str]) -> None:
        """Replace or merge multiple player knowledge entries."""
        for name, knowledge in knowledge_map.items():
            self.update_player_knowledge(name, knowledge)

    def export_players(self) -> Dict[str, str]:
        """Return a shallow copy of the player knowledge mapping."""
        players = self._data.get("players", {}) if isinstance(
            self._data, dict) else {}
        return dict(players) if isinstance(players, dict) else {}

    def save(self) -> None:
        """Persist current knowledge to disk as JSON."""
        serialized = json.dumps(self._data, ensure_ascii=False, indent=2)
        self.file_path.write_text(serialized, encoding="utf-8")

    @property
    def path(self) -> str:
        """Return the checkpoint file path as string."""
        return str(self.file_path)
