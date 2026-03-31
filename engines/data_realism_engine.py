from __future__ import annotations

from .common import load_json, save_json, now_iso


class DataRealismEngine:
    def validate_candidate(self, candidate: dict) -> dict:
        salary = float(candidate.get("salary", 0))
        rent = float(candidate.get("rent", 0))
        city_costs = candidate.get("city_costs", {})
        baseline = sum(float(city_costs.get(k, 0)) for k in ["groceries", "utilities", "transport", "insurance", "healthcare_baseline"])

        monthly_salary = salary / 12 if salary else 0
        rent_ratio = (rent / monthly_salary) if monthly_salary else 9
        total_ratio = ((rent + baseline) / monthly_salary) if monthly_salary else 9

        anomalies = []
        if salary <= 0 or rent <= 0:
            anomalies.append("non_positive_salary_or_rent")
        if rent_ratio < 0.12 or rent_ratio > 0.7:
            anomalies.append("rent_salary_ratio_out_of_range")
        if total_ratio > 0.92:
            anomalies.append("total_cost_overload")
        if baseline <= 0:
            anomalies.append("missing_city_baseline")
        salary_dist = city_costs.get("salary_distribution", {})
        rent_dist = city_costs.get("rent_distribution", {})
        if salary_dist:
            p25 = float(salary_dist.get("p25", 0))
            p90 = float(salary_dist.get("p90", 0))
            if p25 and p90 and (salary < p25 * 0.65 or salary > p90 * 1.45):
                anomalies.append("salary_outlier_vs_city_distribution")
        else:
            anomalies.append("unknown_salary_distribution")
        if rent_dist:
            low = float(rent_dist.get("studio", 0))
            high = float(rent_dist.get("three_bed", 0))
            if low and high and (rent < low * 0.7 or rent > high * 1.45):
                anomalies.append("rent_outlier_vs_city_distribution")
        else:
            anomalies.append("unknown_rent_distribution")
        return {
            "allowed": not anomalies,
            "anomalies": anomalies,
            "metrics": {"rent_salary_ratio": round(rent_ratio, 3), "total_cost_ratio": round(total_ratio, 3), "baseline_cost": round(baseline, 2)},
        }

    def run(self, pages: list[dict]) -> dict:
        blocked = []
        for p in pages:
            result = self.validate_candidate({"salary": p.get("salary"), "rent": p.get("rent"), "city_costs": p.get("city_costs", {})})
            if not result["allowed"]:
                blocked.append({"slug": p.get("slug"), **result})
        report = {"updated_at": now_iso(), "checked": len(pages), "blocked": blocked, "decision_allowed": not blocked}
        save_json("indexes/data_realism_index.json", report)
        return report
