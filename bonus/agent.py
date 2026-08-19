"""Minimal hybrid-memory agent built on the Day 19 vector + feature stores."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.search import Searcher


class HybridMemoryAgent:
    def __init__(self, corpus_path: Path | None = None, feast_repo: Path | None = None):
        root = Path(__file__).resolve().parent.parent
        self.searcher = Searcher.from_corpus(corpus_path or root / "data" / "corpus_vn.jsonl")
        self.feast_repo = feast_repo or root / "app" / "feast_repo"
        self.memories: list[dict[str, str]] = []

    def remember(self, text: str, user_id: str = "u_001") -> None:
        self.memories.append({"user_id": user_id, "text": text})

    def _profile(self, user_id: str) -> dict[str, Any]:
        try:
            from feast import FeatureStore
            fs = FeatureStore(repo_path=str(self.feast_repo))
            return fs.get_online_features(
                features=["user_profile_features:preferred_language",
                          "user_profile_features:topic_affinity",
                          "query_velocity_features:queries_last_hour"],
                entity_rows=[{"user_id": user_id}],
            ).to_dict()
        except Exception:
            return {}

    def recall(self, query: str, user_id: str = "u_001") -> str:
        hits = self.searcher.search(query, mode="hybrid", top_k=5)
        profile = self._profile(user_id)
        local = [m["text"] for m in self.memories if m["user_id"] == user_id]
        lines = [f"User: {user_id}", f"Query: {query}",
                 f"Profile: {json.dumps(profile, ensure_ascii=False)}"]
        if local:
            lines.append("Recent saved memories:\n- " + "\n- ".join(local[-5:]))
        lines.append("Retrieved documents:\n" +
                     "\n".join(f"- {h.doc_id}: {h.title}" for h in hits))
        return "\n".join(lines)
