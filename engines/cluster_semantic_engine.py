from __future__ import annotations

import hashlib
import math

from .common import now_iso, save_json


class ClusterSemanticEngine:
    def generate_embeddings(self, items: list[dict]) -> list[dict]:
        embedded = []
        for item in items:
            q = item.get("query", "")
            digest = hashlib.sha256(q.encode("utf-8")).digest()
            vec = [((digest[i % len(digest)] / 255) * 2 - 1) for i in range(32)]
            embedded.append({**item, "embedding": vec})
        return embedded

    def _cosine(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0.0

    def group_by_similarity(self, embedded_items: list[dict], threshold: float = 0.82) -> list[dict]:
        clusters: list[dict] = []
        for item in embedded_items:
            placed = False
            for cluster in clusters:
                sim = self._cosine(item["embedding"], cluster["centroid"])
                if sim >= threshold:
                    cluster["items"].append(item)
                    size = len(cluster["items"])
                    cluster["centroid"] = [((c * (size - 1)) + v) / size for c, v in zip(cluster["centroid"], item["embedding"])]
                    placed = True
                    break
            if not placed:
                clusters.append({"cluster_id": f"semantic-{len(clusters)+1}", "centroid": list(item["embedding"]), "items": [item]})
        return clusters

    def group_keywords(self, embedded_items: list[dict], threshold: float = 0.82) -> list[dict]:
        return self.group_by_similarity(embedded_items, threshold=threshold)

    def build_cluster_index_v2(self, keywords: list[dict]) -> dict:
        embedded = self.generate_embeddings(keywords)
        grouped = self.group_keywords(embedded)
        out_clusters = []
        for cluster in grouped:
            out_clusters.append({
                "cluster_id": cluster["cluster_id"],
                "size": len(cluster["items"]),
                "queries": [i.get("query") for i in cluster["items"][:100]],
                "cities": sorted({i.get("city") for i in cluster["items"] if i.get("city")}),
            })
        out = {"updated_at": now_iso(), "clusters": out_clusters}
        save_json("indexes/cluster_index_v2.json", out)
        return out
