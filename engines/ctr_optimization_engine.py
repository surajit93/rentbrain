class CtrOptimizationEngine:
    def run(self, pages):
        for p in pages:
            p["title"]=f"Can I afford ${int(p['rent'])} rent in {p['city']} on ${int(p['salary'])} salary after tax? ({p['scenario']})"
            p["meta_description"]=f"Instant rent decision for {p['city']}: after-tax income, post-rent cash, risk level, and survival buffer."
        return pages
