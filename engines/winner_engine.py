def get_winners(gsc_data):
    return [p for p in gsc_data if p.get("impressions", 0) > 10]


def generate_support_keywords(keyword):
    return [
        f"{keyword} tips",
        f"{keyword} guide",
        f"{keyword} examples",
        f"{keyword} breakdown",
    ]
