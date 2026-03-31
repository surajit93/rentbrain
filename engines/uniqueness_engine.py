from __future__ import annotations

import hashlib
import math

from .common import load_json, save_json, now_iso


class UniquenessEngine:
    DIMENSIONS = 64

    def _tokens(self, page: dict) -> list[str]:
        text = " ".join(
            [
                str(page.get("title", "")),
                str(page.get("city", "")),
                str(page.get("state", "")),
                str(page.get("scenario", "")),
                str(page.get("intent", "")),
                str(page.get("rent", "")),
                str(page.get("salary", "")),
                str(page.get("source_query", "")),
            ]
        ).lower()
        clean = []
        for token in text.replace("$", " ").replace("-", " ").split():
            token = "".join(ch for ch in token if ch.isalnum() or ch == "_")
            if token:
                clean.append(token)
        return clean

    def _embedding(self, tokens: list[str]) -> list[float]:
        vec = [0.0] * self.DIMENSIONS
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for i in range(self.DIMENSIONS):
                vec[i] += 1.0 if digest[i % len(digest)] % 2 == 0 else -1.0
        return vec

    def _cosine(self, va: list[float], vb: list[float]) -> float:
        dot = sum(a * b for a, b in zip(va, vb))
        na = math.sqrt(sum(a * a for a in va))
        nb = math.sqrt(sum(b * b for b in vb))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def _structural_variation(self, candidate: dict, page: dict) -> float:
        layout_a = tuple(candidate.get("layout", []))
        layout_b = tuple(page.get("layout", []))
        if not layout_a and not layout_b:
            return 0.0
        overlap = len(set(layout_a) & set(layout_b))
        union = max(1, len(set(layout_a) | set(layout_b)))
        return 1 - (overlap / union)

    def _intent_variance(self, candidate: dict, page: dict) -> float:
        same_city = candidate.get("city") == page.get("city")
        same_intent = candidate.get("intent") == page.get("intent")
        same_scenario = candidate.get("scenario") == page.get("scenario")
        if same_city and same_intent and same_scenario:
            return 0.0
        if same_city and same_intent:
            return 0.35
        if same_city:
            return 0.65
        return 1.0

    def evaluate(self, candidate: dict, existing_pages: list[dict]) -> dict:
        persisted = load_json("indexes/uniqueness_index.json").get("pages", [])
        corpus = existing_pages + [p for p in persisted if p.get("slug") not in {e.get("slug") for e in existing_pages}]
        c_tokens = self._tokens(candidate)
        c_vec = self._embedding(c_tokens)

        max_similarity = 0.0
        min_structural_variation = 1.0
        min_intent_variance = 1.0
        for page in corpus:
            p_vec = self._embedding(self._tokens(page))
            sim = self._cosine(c_vec, p_vec)
            max_similarity = max(max_similarity, sim)
            min_structural_variation = min(min_structural_variation, self._structural_variation(candidate, page))
            min_intent_variance = min(min_intent_variance, self._intent_variance(candidate, page))

        uniqueness_score = (
            (1 - max_similarity) * 0.6
            + min_structural_variation * 0.2
            + min_intent_variance * 0.2
        )
        uniqueness_score = round(max(0.0, min(1.0, uniqueness_score)), 4)

        blocked = max_similarity > 0.9 or uniqueness_score < 0.65
        return {
            "score": uniqueness_score,
            "max_similarity": round(max_similarity, 4),
            "structural_variation": round(min_structural_variation, 4),
            "intent_variance": round(min_intent_variance, 4),
            "blocked": blocked,
            "reason": "high_similarity" if max_similarity > 0.9 else ("low_uniqueness" if uniqueness_score < 0.65 else "ok"),
        }

    def score(self, candidate: dict, existing_pages: list[dict]) -> float:
        return self.evaluate(candidate, existing_pages)["score"]

    def save_memory(self, pages: list[dict]):
        compact = []
        for p in pages:
            compact.append(
                {
                    "slug": p.get("slug"),
                    "title": p.get("title"),
                    "city": p.get("city"),
                    "state": p.get("state"),
                    "scenario": p.get("scenario"),
                    "intent": p.get("intent"),
                    "rent": p.get("rent"),
                    "salary": p.get("salary"),
                    "layout": p.get("layout", []),
                    "source_query": p.get("source_query"),
                }
            )
        save_json("indexes/uniqueness_index.json", {"updated_at": now_iso(), "pages": compact})
