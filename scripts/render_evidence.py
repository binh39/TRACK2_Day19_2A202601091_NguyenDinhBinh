"""Render compact PNG evidence cards from executed notebook text outputs."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "submission" / "screenshots"

TARGETS = {
    "01_embeddings_index": ("Indexed:", "Query (paraphrase):", "Top-5:"),
    "02_hybrid_search_rrf": ("Precision@10", "type", "mixed"),
    "03_search_api_benchmark": ("latency_ms:", "P50", "Hybrid P99"),
    "04_feast_feature_store": ("Created feature view", "Materializing", "PIT"),
    "05_filtered_search": ("filter", "fetch_k", "fANN"),
    "06_agent_retrieval": ("strategy", "agentic", "features"),
    "07_semantic_cache": ("ngưỡng", "0.80", "namespaced=True"),
    "08_feature_engineering": ("target-naive", "dòng bị rò", "amount_vs_avg"),
}


def font(size: int):
    candidates = [
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def outputs(name: str) -> str:
    nb = json.loads((ROOT / "notebooks" / f"{name}.ipynb").read_text(encoding="utf-8"))
    chunks = []
    for cell in nb["cells"]:
        for out in cell.get("outputs", []):
            if "text" in out:
                chunks.append("".join(out["text"]))
    return "\n".join(chunks)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    title_font, body_font = font(28), font(18)
    for name, needles in TARGETS.items():
        raw = outputs(name)
        lines = raw.splitlines()
        selected = []
        for i, line in enumerate(lines):
            if any(n.lower() in line.lower() for n in needles):
                selected.extend(lines[max(0, i - 1): min(len(lines), i + 6)])
        if not selected:
            selected = lines[:30]
        deduped = list(dict.fromkeys(x for x in selected if x.strip()))
        wrapped = []
        for line in deduped[:45]:
            wrapped.extend(textwrap.wrap(line, width=105) or [""])
        height = max(180, 90 + 25 * len(wrapped))
        image = Image.new("RGB", (1800, height), "#101827")
        draw = ImageDraw.Draw(image)
        draw.text((45, 25), f"Day 19 Evidence — {name}", fill="#7dd3fc", font=title_font)
        y = 85
        for line in wrapped:
            draw.text((50, y), line, fill="#e5e7eb", font=body_font)
            y += 25
        image.save(OUT / f"{name}.png")


if __name__ == "__main__":
    main()
