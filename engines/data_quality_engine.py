from __future__ import annotations

from pathlib import Path

from .common import ROOT, load_json, save_json, now_iso


class DataQualityEngine:
    REQUIRED_STATE_FIELDS = {
        "state",
        "name",
        "rent_distribution",
        "salary_distribution",
        "tax_model",
        "groceries",
        "utilities",
        "transport",
        "insurance",
        "healthcare_baseline",
        "savings_ratio",
        "inflation_factor",
        "cities",
    }
    REQUIRED_CITY_FIELDS = {
        "name",
        "tier",
        "population",
        "rent_distribution",
        "salary_distribution",
        "tax_model",
        "groceries",
        "utilities",
        "transport",
        "insurance",
        "healthcare_baseline",
        "savings_ratio",
        "inflation_factor",
    }
    REQUIRED_DISTS = {"studio", "one_bed", "two_bed", "three_bed"}
    REQUIRED_SALARY = {"p25", "p50", "p75", "p90"}
    ALL_STATES = {
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    }

    def _validate_numeric(self, node: dict, fields: set[str], path: str, issues: list[dict]):
        for fld in fields:
            if fld not in node:
                continue
            val = node[fld]
            if not isinstance(val, (int, float)):
                issues.append({"path": f"{path}.{fld}", "issue": "non_numeric"})
            elif val <= 0:
                issues.append({"path": f"{path}.{fld}", "issue": "non_positive"})

    def _validate_realism(self, node: dict, path: str, issues: list[dict]):
        rents = node.get("rent_distribution", {})
        salaries = node.get("salary_distribution", {})
        if rents and salaries:
            avg_rent = (rents.get("one_bed", 0) + rents.get("two_bed", 0)) / 2
            monthly_salary = salaries.get("p50", 0) / 12
            ratio = (avg_rent / monthly_salary) if monthly_salary else 9
            if ratio > 0.6 or ratio < 0.12:
                issues.append({"path": f"{path}.rent_salary_ratio", "issue": "out_of_range", "value": round(ratio, 3)})

        costs = sum(
            node.get(k, 0)
            for k in ["groceries", "utilities", "transport", "insurance", "healthcare_baseline"]
        )
        if salaries.get("p50", 0):
            cost_ratio = costs / (salaries["p50"] / 12)
            if cost_ratio > 0.75:
                issues.append({"path": f"{path}.baseline_cost_ratio", "issue": "too_high", "value": round(cost_ratio, 3)})

        inflation = node.get("inflation_factor", 1)
        if inflation < 0.8 or inflation > 1.3:
            issues.append({"path": f"{path}.inflation_factor", "issue": "anomaly"})

    def run(self) -> dict:
        states_dir = ROOT / "data" / "states"
        files = sorted(states_dir.glob("*.json"))
        found = set()
        missing_fields = []
        schema_issues = []
        unrealistic = []
        tier_coverage = {}

        for f in files:
            data = load_json(str(f.relative_to(ROOT)))
            code = data.get("state")
            if code:
                found.add(code)
            missing = sorted(self.REQUIRED_STATE_FIELDS - set(data.keys()))
            if missing:
                missing_fields.append({"state_file": f.name, "missing": missing})

            rd = data.get("rent_distribution", {})
            sd = data.get("salary_distribution", {})
            tm = data.get("tax_model", {})
            if set(rd.keys()) != self.REQUIRED_DISTS:
                schema_issues.append({"state_file": f.name, "field": "rent_distribution", "keys": sorted(rd.keys())})
            if set(sd.keys()) != self.REQUIRED_SALARY:
                schema_issues.append({"state_file": f.name, "field": "salary_distribution", "keys": sorted(sd.keys())})
            if not {"effective_income_tax_rate", "state_income_tax_rate", "sales_tax_rate"}.issubset(tm.keys()):
                schema_issues.append({"state_file": f.name, "field": "tax_model", "keys": sorted(tm.keys())})

            self._validate_numeric(data, {"groceries", "utilities", "transport", "insurance", "healthcare_baseline", "savings_ratio", "inflation_factor"}, f.name, unrealistic)
            self._validate_realism(data, f.name, unrealistic)
            if rd and not (rd.get("studio", 0) < rd.get("one_bed", 0) < rd.get("two_bed", 0) < rd.get("three_bed", 0)):
                unrealistic.append({"path": f"{f.name}.rent_distribution", "issue": "non_monotonic"})
            if sd and not (sd.get("p25", 0) < sd.get("p50", 0) < sd.get("p75", 0) < sd.get("p90", 0)):
                unrealistic.append({"path": f"{f.name}.salary_distribution", "issue": "non_monotonic"})

            cities = data.get("cities", [])
            major = sum(1 for c in cities if c.get("tier") == "major")
            mid = sum(1 for c in cities if c.get("tier") == "mid")
            tier_coverage[f.name] = {"major": major, "mid": mid}
            if major < 1 or mid < 1:
                schema_issues.append({"state_file": f.name, "field": "cities", "issue": "missing_major_or_mid"})

            for idx, city in enumerate(cities):
                cmiss = sorted(self.REQUIRED_CITY_FIELDS - set(city.keys()))
                if cmiss:
                    missing_fields.append({"state_file": f.name, "city": city.get("name", idx), "missing": cmiss})
                if set(city.get("rent_distribution", {}).keys()) != self.REQUIRED_DISTS:
                    schema_issues.append({"state_file": f.name, "city": city.get("name", idx), "field": "rent_distribution"})
                if set(city.get("salary_distribution", {}).keys()) != self.REQUIRED_SALARY:
                    schema_issues.append({"state_file": f.name, "city": city.get("name", idx), "field": "salary_distribution"})
                self._validate_realism(city, f"{f.name}.cities[{idx}]", unrealistic)

        missing_states = sorted(self.ALL_STATES - found)
        report = {
            "updated_at": now_iso(),
            "state_files": len(files),
            "missing_states": missing_states,
            "missing_fields": missing_fields,
            "schema_inconsistencies": schema_issues,
            "unrealistic_values": unrealistic,
            "tier_coverage": tier_coverage,
            "valid": not (missing_states or missing_fields or schema_issues or unrealistic),
            "decision_allowed": not (missing_states or missing_fields or schema_issues or unrealistic),
        }
        save_json("indexes/data_quality_index.json", report)
        return report
