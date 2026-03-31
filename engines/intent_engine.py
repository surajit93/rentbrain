def classify(keyword):
    if "how" in keyword:
        return "informational"
    if "calculator" in keyword:
        return "calculator"
    if "best" in keyword:
        return "comparison"
    return "general"
