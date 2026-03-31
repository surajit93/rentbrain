from __future__ import annotations

from .common import load_json, now_iso, save_json


class LearningLoopEngine:
    def store_historical_performance(self) -> dict:
        history = load_json("indexes/learning_history_v2.json")
        perf = load_json("indexes/performance_index.json")
        rows = history.get("history", []) if isinstance(history, dict) else []
        rows.append({"at": now_iso(), "site": perf.get("site", {}), "pages": perf.get("pages", [])})
        rows = rows[-180:]
        doc = {"updated_at": now_iso(), "history": rows}
        save_json("indexes/learning_history_v2.json", doc)
        return doc

    def detect_winning_patterns(self) -> dict:
        perf = load_json("indexes/performance_index.json")
        winners = [p for p in perf.get("pages", []) if p.get("impressions", 0) >= 20 and p.get("ctr", 0) >= 0.04]
        return {"count": len(winners), "top": sorted(winners, key=lambda x: x.get("ctr", 0), reverse=True)[:25]}

    def detect_losing_patterns(self) -> dict:
        perf = load_json("indexes/performance_index.json")
        losers = [p for p in perf.get("pages", []) if p.get("impressions", 0) >= 20 and p.get("ctr", 0) < 0.015]
        return {"count": len(losers), "top": sorted(losers, key=lambda x: x.get("ctr", 0))[:25]}

    def adjust_strategy_signals(self) -> dict:
        winning = self.detect_winning_patterns()
        losing = self.detect_losing_patterns()
        signal = {
            "updated_at": now_iso(),
            "winning_count": winning["count"],
            "losing_count": losing["count"],
            "scale_bias": "increase" if winning["count"] > losing["count"] else "decrease",
            "ctr_floor_suggested": 0.04 if winning["count"] >= 10 else 0.03,
        }
        save_json("indexes/strategy_signals_v2.json", signal)
        return signal
