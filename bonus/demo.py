"""Five-query bonus demo. Run from the repository root with the lab venv."""
from __future__ import annotations

from agent import HybridMemoryAgent


def main() -> None:
    agent = HybridMemoryAgent()
    agent.remember("Tôi đang học về tối ưu chi phí hạ tầng cloud.")
    agent.remember("Tôi thích tài liệu tiếng Việt có ví dụ thực tế.")
    queries = [
        "What have I read about Kubernetes?",
        "Recommend what to read next",
        "What am I focused on lately?",
        "Documents about scaling infrastructure?",
        "Give me a cloud security summary",
    ]
    for i, query in enumerate(queries, 1):
        print(f"\n===== Demo query {i}: {query} =====")
        print(agent.recall(query))


if __name__ == "__main__":
    main()
