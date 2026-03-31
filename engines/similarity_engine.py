from difflib import SequenceMatcher


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def is_duplicate(new_content, existing_contents, threshold=0.7):
    for content in existing_contents:
        if similarity(new_content, content) > threshold:
            return True
    return False
