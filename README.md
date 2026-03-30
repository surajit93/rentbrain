
# Rent Decision Platform

Automated, strategy-governed programmatic SEO system for US rent affordability long-tail clusters.

## Quickstart

```bash
python scripts/run_pipeline.py
```

## Architecture
- `engines/strategy_engine.py` is master control.
- All engines are deterministic and governed by `config.json` and `/instructions`.
- Scaling is blocked unless indexing/CTR/impressions thresholds are met.
