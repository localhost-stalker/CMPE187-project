import re
from difflib import SequenceMatcher


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def similarity(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def extract_field(response, field_name):
    pattern = rf"{re.escape(field_name)}\s*:\s*(.*?)(?=\s*\|\s*[A-Za-z ]+\s*:|$)"
    match = re.search(pattern, response, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""


def best_similarity(expected_options, actual):
    if isinstance(expected_options, str):
        expected_options = [expected_options]
    if not expected_options:
        return 0.0
    return max(similarity(expected, actual) for expected in expected_options)


def grade_response(test, response):
    text = normalize(response)
    grader = test["grader"]

    if grader == "dialect":
        transcript = extract_field(response, "Transcript")
        accent = extract_field(response, "Accent")
        transcript_score = best_similarity(
            test.get("expected_transcripts", []),
            transcript if transcript else response,
        )

        accent_text = normalize(accent if accent else response)
        accent_exact = any(
            phrase in accent_text
            for phrase in ["mandarin", "chinese accent", "chinese accented"]
        )
        accent_related = any(
            phrase in accent_text
            for phrase in ["east asian", "non native", "asian accent"]
        )

        if transcript_score >= 0.80 and accent_exact:
            return "Pass"
        if transcript_score >= 0.65 and (accent_exact or accent_related):
            return "Partial Pass"
        if transcript_score >= 0.80 or accent_exact:
            return "Partial Pass"
        return "Fail"

    if grader == "transcript":
        score = similarity(test["expected"], response)
        if score >= 0.85:
            return "Pass"
        if score >= 0.65:
            return "Partial Pass"
        return "Fail"

    if grader == "animal":
        if "canary" in text or "serinus canaria" in text:
            return "Pass"
        if "bird" in text:
            return "Partial Pass"
        return "Fail"

    if grader == "instruments":
        expected = {
            normalize(instrument)
            for instrument in test.get("expected_instruments", [])
        }
        detected = {
            instrument
            for instrument in expected
            if instrument in text
        }

        if expected and detected == expected:
            return "Pass"
        if detected:
            return "Partial Pass"
        return "Fail"

    if grader == "emotion":
        primary_text = normalize(extract_field(response, "Primary"))
        secondary_text = normalize(extract_field(response, "Secondary"))

        primary_labels = ["anxiety", "anxious", "tense", "tension", "nervous"]
        secondary_labels = ["admiration", "awe", "awestruck", "amazed", "amazement"]

        primary_correct = any(word in primary_text for word in primary_labels)
        secondary_correct = any(word in secondary_text for word in secondary_labels)

        if primary_correct and secondary_correct:
            return "Pass"

        overall_primary = any(word in text for word in primary_labels)
        overall_secondary = any(word in text for word in secondary_labels)
        if primary_correct or secondary_correct or overall_primary or overall_secondary:
            return "Partial Pass"
        return "Fail"

    if grader == "pitch":
        return "Pass" if re.search(r"\bb\s*5\b", text) else "Fail"

    if grader == "disfluency":
        corrected = extract_field(response, "Corrected text")
        mistakes = extract_field(response, "Mistakes")

        comparison_text = corrected if corrected else response
        score = similarity(test["expected"], comparison_text)
        has_mistake_analysis = bool(mistakes.strip())

        if score >= 0.85 and has_mistake_analysis:
            return "Pass"
        if score >= 0.70:
            return "Partial Pass"
        if score >= 0.55 and has_mistake_analysis:
            return "Partial Pass"
        return "Fail"

    if grader == "genre":
        return "Pass" if re.search(r"\bjazz\b", text) else "Fail"

    raise ValueError(f"Unknown grader type: {grader}")
