from __future__ import annotations

from .uniqueness_engine import UniquenessEngine


class ContentUniquenessEngine:
    def __init__(self):
        self._engine = UniquenessEngine()

    def compute_similarity(self, page_a: dict, page_b: dict) -> float:
        va = self._engine._embedding(self._engine._tokens(page_a))
        vb = self._engine._embedding(self._engine._tokens(page_b))
        return round(self._engine._cosine(va, vb), 4)

    def enforce_uniqueness_threshold(self, candidate: dict, corpus: list[dict], threshold: float = 0.75) -> dict:
        eval_result = self._engine.evaluate(candidate, corpus)
        eval_result["threshold"] = threshold
        eval_result["allowed"] = (not eval_result.get("blocked")) and eval_result.get("score", 0) >= threshold
        return eval_result
