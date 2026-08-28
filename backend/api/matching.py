"""Rule-based matcher for free-text enquiries.

Deliberately simple and transparent: matches keyword phrases against the
free text and scores each category by how many of its keywords appear.
No LLM call, no hidden logic — see docs/PLAN.md for the reasoning.
"""

from .models import EnquiryCategory

NOT_SURE_SLUG = "not-sure"

# Number of matched keyword phrases -> confidence score.
_CONFIDENCE_BY_SCORE = {1: 0.5, 2: 0.75}
_MAX_CONFIDENCE = 0.95
MAX_MATCHES = 3


def _confidence_for_score(score):
    if score >= 3:
        return _MAX_CONFIDENCE
    return _CONFIDENCE_BY_SCORE.get(score, 0.0)


def match_text(text):
    """Score every category (except "not sure") against free text.

    Returns a list of (category, score, confidence) tuples, sorted by score
    descending, limited to categories that matched at least one keyword.
    """
    text_lower = text.lower()
    scored = []
    for category in EnquiryCategory.objects.exclude(slug=NOT_SURE_SLUG):
        keywords = [k.strip().lower() for k in category.keywords.split(",") if k.strip()]
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            scored.append((category, score, _confidence_for_score(score)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:MAX_MATCHES]
