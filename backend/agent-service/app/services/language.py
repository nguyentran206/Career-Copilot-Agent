import re

from app.schemas.analysis import LanguageInfo

try:
    from langdetect import DetectorFactory, detect_langs

    DetectorFactory.seed = 0
except ImportError:  # The heuristic remains available during partial installs.
    detect_langs = None


VIETNAMESE_DIACRITICS = re.compile(
    r"[ăâđêôơưàáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩị"
    r"òóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ]",
    re.IGNORECASE,
)
VIETNAMESE_WORDS = {
    "và",
    "có",
    "kinh",
    "nghiệm",
    "phát",
    "triển",
    "xây",
    "dựng",
    "yêu",
    "cầu",
    "bắt",
    "buộc",
    "ưu",
    "tiên",
    "lợi",
    "thế",
    "kỹ",
    "năng",
    "công",
    "việc",
}
ENGLISH_WORDS = {
    "and",
    "with",
    "experience",
    "required",
    "preferred",
    "build",
    "develop",
    "skills",
    "role",
    "work",
    "project",
    "engineer",
    "developer",
    "analyst",
}


def detect_language(text: str) -> LanguageInfo:
    tokens = re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)
    vietnamese_hits = sum(token in VIETNAMESE_WORDS for token in tokens)
    english_hits = sum(token in ENGLISH_WORDS for token in tokens)
    if VIETNAMESE_DIACRITICS.search(text):
        vietnamese_hits += 3

    probability_by_language: dict[str, float] = {}
    if detect_langs is not None:
        try:
            for candidate in detect_langs(text):
                if candidate.prob >= 0.10:
                    probability_by_language[candidate.lang.lower()] = round(
                        candidate.prob,
                        2,
                    )
        except Exception:
            probability_by_language = {}

    detected: list[str] = list(probability_by_language)
    if vietnamese_hits:
        probability_by_language["vi"] = max(
            probability_by_language.get("vi", 0.0),
            0.60,
        )
        if "vi" not in detected:
            detected.append("vi")
    if english_hits:
        probability_by_language["en"] = max(
            probability_by_language.get("en", 0.0),
            0.60,
        )
        if "en" not in detected:
            detected.append("en")
    if not detected:
        return LanguageInfo(
            primary_language="unknown",
            detected_languages=[],
            is_mixed_language=False,
            confidence=0.0,
        )

    primary = max(probability_by_language, key=probability_by_language.get)
    if vietnamese_hits > english_hits and vietnamese_hits >= 3:
        primary = "vi"
    elif english_hits > vietnamese_hits and english_hits >= 3:
        primary = "en"
    return LanguageInfo(
        primary_language=primary,
        detected_languages=detected,
        is_mixed_language=len(detected) > 1,
        confidence=probability_by_language.get(primary, 0.0),
    )


def needs_english_canonicalization(language: LanguageInfo) -> bool:
    return any(code != "en" for code in language.detected_languages) or (
        language.primary_language not in {"en", "unknown"}
    )
