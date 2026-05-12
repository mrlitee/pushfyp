"""Violation categories and the Instagram Community Guidelines clauses they map to.

Keep this file small and auditable. Adding a category must be a conscious act.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    key: str
    label_id: str           # Bahasa Indonesia
    label_en: str           # English
    ig_report_path: str     # how to reach the correct report form in-app
    guideline_ref: str      # which Community Guideline clause applies
    extra_channels: tuple[str, ...]  # non-IG channels to also notify


CATEGORIES: dict[str, Category] = {
    "scam": Category(
        key="scam",
        label_id="Penipuan / Scam",
        label_en="Fraud / Scam",
        ig_report_path="Profile -> ... -> Report -> It's posting content that shouldn't be on Instagram -> Scam or fraud",
        guideline_ref="Community Guidelines: Fraud and Spam",
        extra_channels=(
            "https://www.ic3.gov/ (FBI IC3, if victim is in the US)",
            "https://aduanbrti.kominfo.go.id/ (Kominfo, Indonesia)",
            "Local police cyber unit",
        ),
    ),
    "threat": Category(
        key="threat",
        label_id="Ancaman Kekerasan",
        label_en="Violent threat",
        ig_report_path="Profile/Post -> ... -> Report -> Violence or dangerous organizations -> Threat of violence",
        guideline_ref="Community Guidelines: Violence and Incitement",
        extra_channels=(
            "Local police (emergency if imminent)",
            "https://patrolisiber.id/ (Bareskrim Polri cyber, Indonesia)",
        ),
    ),
    "doxxing": Category(
        key="doxxing",
        label_id="Doxxing / Pembocoran data pribadi",
        label_en="Doxxing / Private information exposure",
        ig_report_path="Profile/Post -> ... -> Report -> It's posting content that shouldn't be on Instagram -> Sharing private information",
        guideline_ref="Privacy Violations policy",
        extra_channels=(
            "https://help.instagram.com/contact/504521742987441 (IG privacy form)",
            "https://aduanbrti.kominfo.go.id/ (Kominfo, Indonesia)",
        ),
    ),
    "harassment": Category(
        key="harassment",
        label_id="Pelecehan / Perundungan",
        label_en="Harassment / Bullying",
        ig_report_path="Profile/Post -> ... -> Report -> Bullying or harassment",
        guideline_ref="Community Guidelines: Bullying and Harassment",
        extra_channels=(
            "https://help.instagram.com/contact/584460464982589 (IG harassment form)",
        ),
    ),
    "impersonation": Category(
        key="impersonation",
        label_id="Impersonasi / Akun palsu",
        label_en="Impersonation / Fake account",
        ig_report_path="Profile -> ... -> Report -> Report account -> It's pretending to be someone else",
        guideline_ref="Community Guidelines: Authentic Identity",
        extra_channels=(
            "https://help.instagram.com/contact/636276399721841 (IG impersonation form)",
        ),
    ),
    "csam": Category(
        key="csam",
        label_id="Eksploitasi seksual anak (CSAM)",
        label_en="Child sexual abuse material (CSAM)",
        ig_report_path="Profile/Post -> ... -> Report -> Nudity or sexual activity -> Involves a child",
        guideline_ref="Community Guidelines: Child Safety (zero tolerance)",
        extra_channels=(
            "https://report.cybertip.org/ (NCMEC CyberTipline) -- PRIORITY",
            "Local police / Interpol",
            "https://aduanbrti.kominfo.go.id/ (Kominfo, Indonesia)",
        ),
    ),
}


def list_categories() -> list[str]:
    return list(CATEGORIES.keys())


def get(key: str) -> Category:
    if key not in CATEGORIES:
        raise KeyError(
            f"Unknown category '{key}'. Available: {', '.join(list_categories())}"
        )
    return CATEGORIES[key]
