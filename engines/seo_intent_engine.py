from __future__ import annotations

from dataclasses import dataclass
import hashlib


INTENT_PAGE_TYPES = {
    "average_rent": {
        "slug": "average-rent-in-{city_slug}",
        "cluster": "Rent",
        "title": "Average Rent in {city}, {state} ({year})",
    },
    "cost_of_living": {
        "slug": "cost-of-living-{city_slug}",
        "cluster": "Cost of Living",
        "title": "Cost of Living in {city}, {state} ({year})",
    },
    "rent_trends": {
        "slug": "rent-trends-{city_slug}",
        "cluster": "Trends",
        "title": "Rent Trends in {city}, {state} ({year})",
    },
    "rent_vs_income": {
        "slug": "rent-vs-income-{city_slug}",
        "cluster": "Affordability",
        "title": "Rent vs Income in {city}, {state} ({year})",
    },
}


@dataclass(frozen=True)
class CityContext:
    city: str
    state: str
    city_slug: str
    median_rent: float
    median_salary: float
    ratio: float
    national_rent: float
    national_salary: float
    national_ratio: float


def city_slug(city: str) -> str:
    return city.lower().replace(" ", "-")


def _stable_variant_key(*values: str) -> int:
    digest = hashlib.sha256("|".join(values).encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def build_city_context(city_row: dict, city_index: list[dict]) -> CityContext:
    national_rent = sum(float(c.get("median_rent", 0)) for c in city_index) / max(len(city_index), 1)
    national_salary = sum(float(c.get("median_salary", 0)) for c in city_index) / max(len(city_index), 1)
    median_rent = float(city_row.get("median_rent", 0))
    median_salary = float(city_row.get("median_salary", 0))
    ratio = (median_rent * 12) / max(median_salary, 1)
    national_ratio = (national_rent * 12) / max(national_salary, 1)
    return CityContext(
        city=str(city_row.get("city", "")),
        state=str(city_row.get("state", "")),
        city_slug=city_slug(str(city_row.get("city", ""))),
        median_rent=median_rent,
        median_salary=median_salary,
        ratio=ratio,
        national_rent=national_rent,
        national_salary=national_salary,
        national_ratio=national_ratio,
    )


def insight_blocks(context: CityContext, page_kind: str) -> list[dict]:
    variant = _stable_variant_key(context.city, context.state, page_kind) % 3
    rent_gap = round(context.median_rent - context.national_rent, 0)
    affordability_delta = round((context.ratio - context.national_ratio) * 100, 1)
    direction = "up" if rent_gap > 0 else "down"

    trend_lines = [
        f"Modeled signals indicate {context.city} rent pressure is tilted {direction} versus the national baseline.",
        f"Current modeled trajectory shows {context.city} rent momentum moving {direction} relative to national rent benchmarks.",
        f"Trend indicators suggest {context.city} rents are tracking {direction} against broader U.S. rent patterns.",
    ]
    comparison_lines = [
        f"The city median rent is ${int(context.median_rent):,} compared with the national modeled average of ${int(context.national_rent):,}.",
        f"Against a national modeled rent of ${int(context.national_rent):,}, {context.city} sits at about ${int(context.median_rent):,}.",
        f"Relative to the modeled U.S. average rent (${int(context.national_rent):,}), {context.city} is near ${int(context.median_rent):,}.",
    ]
    affordability_lines = [
        f"Annual rent-to-income load is {context.ratio:.1%}, about {affordability_delta:+.1f} percentage points versus national baseline.",
        f"At roughly {context.ratio:.1%} rent-to-income, affordability is {affordability_delta:+.1f} points against U.S. modeled conditions.",
        f"The modeled rent burden is {context.ratio:.1%}, placing {context.city} {affordability_delta:+.1f} points relative to national burden.",
    ]

    idx = variant
    return [
        {"type": "trend", "title": f"{context.city} rent trend signal", "content": trend_lines[idx]},
        {"type": "comparison", "title": f"{context.city} vs U.S. rent average", "content": comparison_lines[idx]},
        {"type": "affordability", "title": f"{context.city} affordability context", "content": affordability_lines[idx]},
    ]


def meta_for_page(context: CityContext, page_title: str, page_kind: str) -> dict:
    desc = (
        f"{page_title}. See modeled rent levels, affordability signals, city-vs-national comparisons, "
        f"and internal links to related {context.city} housing insights."
    )
    return {
        "title": page_title,
        "description": desc,
        "robots": "index,follow",
        "canonical_path": f"/{INTENT_PAGE_TYPES.get(page_kind, {'slug': context.city_slug})['slug'].format(city_slug=context.city_slug)}" if page_kind in INTENT_PAGE_TYPES else f"/{context.city_slug}",
    }


def related_cities(city_row: dict, all_cities: list[dict], count: int = 3) -> list[str]:
    same_state = [c for c in all_cities if c.get("state") == city_row.get("state") and c.get("city") != city_row.get("city")]
    if len(same_state) >= count:
        return [city_slug(c.get("city", "")) for c in same_state[:count]]
    fallback = [c for c in all_cities if c.get("city") != city_row.get("city")][:count]
    return [city_slug(c.get("city", "")) for c in fallback]


def build_intent_links(city_row: dict, all_cities: list[dict]) -> dict:
    slug = city_slug(city_row.get("city", ""))
    intent_links = [
        f"/average-rent-in-{slug}",
        f"/cost-of-living-{slug}",
        f"/rent-trends-{slug}",
        f"/rent-vs-income-{slug}",
    ]
    related = related_cities(city_row, all_cities)
    related_city_links = [f"/rent-benchmark-{c}" for c in related]
    return {
        "intent_pages": intent_links,
        "benchmark_page": f"/rent-benchmark-{slug}",
        "related_city_pages": related_city_links,
    }
