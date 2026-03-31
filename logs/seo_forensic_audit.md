# SEO Forensic Audit Report

## 1) Full System Map

| File | Behavior | Inputs/Outputs | Data Type |
|---|---|---|---|
| `engines/__init__.py` | module helpers | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/analytics_engine.py` | classes: AnalyticsEngine(_load_gsc_export, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | REAL |
| `engines/analytics_real_engine.py` | classes: AnalyticsRealEngine(fetch_gsc_data, normalize_gsc_data, normalize_metrics, map_page_performance, map_page_to_query, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | REAL |
| `engines/authority_content_engine.py` | classes: AuthorityContentEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/authority_growth_engine.py` | classes: AuthorityGrowthEngine(track_backlinks, compute_authority_score, compute_domain_score, track_link_velocity, track_growth_velocity) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/backlink_engine.py` | classes: BacklinkEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/cluster_priority_engine.py` | classes: ClusterPriorityEngine(_cluster_key, _aggregate_perf, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/cluster_semantic_engine.py` | classes: ClusterSemanticEngine(generate_embeddings, _cosine, group_by_similarity, group_keywords, build_cluster_index_v2) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | SIMULATED |
| `engines/common.py` | functions: load_json, save_json, now_iso | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/content_intelligence_engine.py` | classes: ContentIntelligenceEngine(detect_search_intent, match_serp_pattern, analyze_serp_structure, generate_content_variations, adapt_content_structure) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | REAL |
| `engines/content_uniqueness_engine.py` | classes: ContentUniquenessEngine(__init__, compute_similarity, enforce_uniqueness_threshold, block_duplicate_generation) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/crawl_budget_engine.py` | classes: CrawlBudgetEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/ctr_optimization_engine.py` | classes: CtrOptimizationEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/data_quality_engine.py` | classes: DataQualityEngine(_validate_numeric, _validate_realism, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/data_realism_engine.py` | classes: DataRealismEngine(validate_candidate, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/decision_engine.py` | classes: DecisionEngine(evaluate) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/distribution_engine.py` | classes: DistributionEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/embed_engine.py` | classes: EmbedEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/enhanced_system_engine.py` | classes: EnhancedSystemEngine(_load_mode, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | REAL |
| `engines/entity_engine.py` | classes: EntityEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/internal_linking_engine.py` | classes: InternalLinkingEngine(run, build_link_graph, inject_internal_links, optimize_internal_links) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/keyword_engine.py` | classes: KeywordEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/learning_engine.py` | classes: LearningEngine(load, update, save_snapshot) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/learning_loop_engine.py` | classes: LearningLoopEngine(store_historical_performance, store_performance_history, detect_winning_patterns, detect_high_performing_patterns, detect_losing_patterns, detect_low_performing_patterns, adjust_strategy_signals, update_strategy_inputs) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/page_generator_engine.py` | classes: PageGeneratorEngine(_city_profile, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/pruning_engine.py` | classes: PruningEngine(_age_days, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/query_classifier_engine.py` | classes: QueryClassifierEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/regression_engine.py` | classes: RegressionEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/serp_eligibility_engine.py` | classes: SerpEligibilityEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/serp_google_engine.py` | classes: GoogleSerpRecord() \| functions: _normalize_items, fetch_google_serp, fetch_serp, extract_top_results, detect_big_domains, extract_features, compute_difficulty_score, compute_keyword_difficulty, extract_serp_features | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | REAL |
| `engines/serp_intelligence_engine.py` | classes: _DuckResultParser(__init__, handle_starttag, handle_endtag, handle_data); SerpEvaluation(); SerpIntelligenceEngine(_fetch_duckduckgo, _root_domain, _analyze, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | REAL |
| `engines/serp_merged_engine.py` | classes: SerpMergedEngine(__init__, run) \| functions: merge_with_existing_serp, normalize_signals | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | REAL |
| `engines/strategy_controller_engine.py` | classes: StrategyControllerEngine(prioritize_keywords, allocate_content_budget, allocate_generation_budget, decide_cluster_expansion, select_clusters_to_expand, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | REAL |
| `engines/strategy_engine.py` | classes: StrategyEngine(__init__, _seed_queries, _approve_action, _execute_if_approved, _winner_expansions, run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |
| `engines/template_engine.py` | classes: TemplateEngine(run) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | SIMULATED |
| `engines/uniqueness_engine.py` | classes: UniquenessEngine(_tokens, _embedding, _cosine, _structural_variation, _intent_variance, evaluate, score, save_memory) | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | SIMULATED |
| `data/city_index.json` | json object keys: ['cities'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/cost_models.json` | json object keys: ['cost_components'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/rent_distributions.json` | json object keys: ['bands'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/AK.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/AL.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/AR.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/AZ.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/CA.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/CO.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/CT.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/DE.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/FL.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/GA.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/HI.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/IA.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/ID.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/IL.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/IN.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/KS.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/KY.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/LA.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/MA.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/MD.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/ME.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/MI.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/MN.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/MO.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/MS.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/MT.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/NC.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/ND.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/NE.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/NH.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/NJ.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/NM.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/NV.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/NY.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/OH.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/OK.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/OR.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/PA.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/RI.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/SC.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/SD.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/TN.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/TX.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/UT.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/VA.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/VT.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/WA.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/WI.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/WV.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/states/WY.json` | json object keys: ['state', 'name', 'rent_distribution', 'salary_distribution', 'tax_model', 'groceries', 'utilities', 'transport'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `data/tax_models.json` | json object keys: ['effective_tax_rates'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/cluster_index.json` | json object keys: ['updated_at', 'clusters'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/cluster_index_v2.json` | json object keys: ['updated_at', 'clusters'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/crawl_budget_index.json` | json object keys: ['updated_at', 'indexing_rate', 'impressions_trend', 'status', 'reason', 'target_new_pages_per_day', 'sitemap_segment'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/data_quality_index.json` | json object keys: ['updated_at', 'state_files', 'missing_states', 'missing_fields', 'schema_inconsistencies', 'unrealistic_values', 'tier_coverage', 'valid'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/data_realism_index.json` | json object keys: ['updated_at', 'checked', 'blocked', 'decision_allowed'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/entity_index.json` | json object keys: ['entities'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/internal_link_index.json` | json object keys: ['updated_at', 'links', 'winner_slugs', 'suppressed'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/keyword_index.json` | json object keys: ['keywords', 'updated_at'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/keyword_index_v2.json` | json object keys: ['updated_at', 'keywords'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/learning_index.json` | json object keys: ['updated_at', 'learning'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/page_index.json` | json object keys: ['pages', 'updated_at'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/performance_index.json` | json object keys: ['updated_at', 'source', 'data_status', 'decision_allowed', 'pages', 'site'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/serp_index.json` | json object keys: ['queries', 'updated_at', 'provider'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `indexes/strategy.json` | json object keys: ['version', 'started_at', 'cycles', 'status', 'last_run', 'scale_allowed', 'data_quality', 'learning'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `instructions/authority_instructions.json` | json object keys: ['count_target', 'required'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `instructions/distribution_instructions.json` | json object keys: ['channels', 'rules'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `instructions/interlinking_instructions.json` | json object keys: ['rules'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `instructions/keyword_instructions.json` | json object keys: ['rules'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `instructions/page_generation_instructions.json` | json object keys: ['required', 'title_pattern'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `instructions/pruning_instructions.json` | json object keys: ['rules'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `instructions/serp_instructions.json` | json object keys: ['allow_signals', 'deny_signals'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `instructions/template_instructions.json` | json object keys: ['variants', 'min_structure_variance'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `instructions/update_instructions.json` | json object keys: ['frequency', 'tasks'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `templates/authority_template.md` | markdown template/content | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `templates/page_template.md` | markdown template/content | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/austin-alone-rent-1800-salary-72000-affordability.json` | json object keys: ['slug', 'city', 'state', 'salary', 'rent', 'scenario', 'intent', 'template'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/can-i-afford-1650-rent-in-columbus-68000-salary-salary_sufficiency.json` | json object keys: ['slug', 'city', 'state', 'salary', 'rent', 'scenario', 'title', 'calculator'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/can-i-afford-1650-rent-in-phoenix-68000-salary-salary_sufficiency.json` | json object keys: ['slug', 'city', 'state', 'salary', 'rent', 'scenario', 'title', 'calculator'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/can-i-afford-1650-rent-in-raleigh-68000-salary-salary_sufficiency.json` | json object keys: ['slug', 'city', 'state', 'salary', 'rent', 'scenario', 'title', 'calculator'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/can-i-afford-1650-rent-in-tampa-68000-salary-salary_sufficiency.json` | json object keys: ['slug', 'city', 'state', 'salary', 'rent', 'scenario', 'title', 'calculator'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/can-i-afford-1800-rent-in-austin-72000-salary-salary_sufficiency.json` | json object keys: ['slug', 'city', 'state', 'salary', 'rent', 'scenario', 'title', 'calculator'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/columbus-family-rent-1450-salary-62000-affordability.json` | json object keys: ['slug', 'city', 'state', 'salary', 'rent', 'scenario', 'intent', 'template'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/phoenix-alone-rent-1650-salary-68000-affordability.json` | json object keys: ['slug', 'city', 'state', 'salary', 'rent', 'scenario', 'intent', 'template'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/raleigh-roommates-rent-1600-salary-70000-affordability.json` | json object keys: ['slug', 'city', 'state', 'salary', 'rent', 'scenario', 'intent', 'template'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/sample-austin-affordability.html` | html page artifact | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `pages/tampa-alone-rent-1700-salary-65000-affordability.json` | json object keys: ['slug', 'city', 'state', 'salary', 'rent', 'scenario', 'intent', 'template'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-01.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-02.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-03.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-04.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-05.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-06.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-07.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-08.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-09.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-10.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-11.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-12.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-13.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-14.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-15.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-16.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-17.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-18.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-19.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-20.json` | json object keys: ['slug', 'title', 'structured_data', 'citations', 'analysis_depth'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-austin.json` | json object keys: ['slug', 'title', 'sections', 'dataset', 'structured_data', 'citations', 'word_count_target', 'updated_at'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-columbus.json` | json object keys: ['slug', 'title', 'sections', 'dataset', 'structured_data', 'citations', 'word_count_target', 'updated_at'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-phoenix.json` | json object keys: ['slug', 'title', 'sections', 'dataset', 'structured_data', 'citations', 'word_count_target', 'updated_at'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-raleigh.json` | json object keys: ['slug', 'title', 'sections', 'dataset', 'structured_data', 'citations', 'word_count_target', 'updated_at'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/rent-benchmark-tampa.json` | json object keys: ['slug', 'title', 'sections', 'dataset', 'structured_data', 'citations', 'word_count_target', 'updated_at'] | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `authority_pages/sample-rent-benchmarks.md` | markdown template/content | Input: n/a (repository artifact); Output: consumed by engines/scripts | STATIC |
| `scripts/bootstrap.py` | module helpers | Input: CLI invocation; Output: orchestrated run + generated artifacts | STATIC |
| `scripts/run_pipeline.py` | module helpers | Input: CLI invocation; Output: orchestrated run + generated artifacts | STATIC |
| `scripts/run_pipeline_v2.py` | module helpers | Input: CLI invocation; Output: orchestrated run + generated artifacts | STATIC |
| `config/system_mode.json` | json object keys: ['mode'] | Input: local file/env/runtime args; Output: transformed data/index/log artifacts | STATIC |

## 2) Gap Analysis (File-Mapped)

- `engines/analytics_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/backlink_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/cluster_priority_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/cluster_semantic_engine.py`: Embeddings are hash-based pseudo vectors; no external model-backed semantic signal.
- `engines/cluster_semantic_engine.py`: Hardcoded thresholds reduce adaptability across markets.
- `engines/content_uniqueness_engine.py`: Hardcoded thresholds reduce adaptability across markets.
- `engines/crawl_budget_engine.py`: Hardcoded thresholds reduce adaptability across markets.
- `engines/crawl_budget_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/data_quality_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/data_realism_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/enhanced_system_engine.py`: Hardcoded thresholds reduce adaptability across markets.
- `engines/entity_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/keyword_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/learning_engine.py`: Hardcoded thresholds reduce adaptability across markets.
- `engines/learning_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/page_generator_engine.py`: Hardcoded thresholds reduce adaptability across markets.
- `engines/page_generator_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/serp_google_engine.py`: Graceful fallback can lead to partial/no data states without retries or queueing.
- `engines/serp_intelligence_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/strategy_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.
- `engines/template_engine.py`: Graceful fallback can lead to partial/no data states without retries or queueing.
- `engines/uniqueness_engine.py`: Embeddings are hash-based pseudo vectors; no external model-backed semantic signal.
- `engines/uniqueness_engine.py`: Writes baseline indexes directly; limited versioned lineage for experimentation.

## 3) Upgrade Architecture (Additive + Backward Compatible)

- Legacy mode remains unchanged via `config/system_mode.json` = `legacy`.
- Enhanced mode layers V2 engines and V2 indexes (`*_v2.json`) in parallel outputs.
- Pipeline: SERP → scoring → content intelligence + uniqueness → index v2 → analytics real → learning loop → strategy controller → next-cycle budget.