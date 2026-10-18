"""Runtime wording; HA's integration schema has no notification-text category."""

TEXTS = {
    "en": {
        "title": "PlantBased: plant care",
        "water": "Watering due",
        "fertilize": "Fertilizing due",
        "all_watered": "All watered",
        "all_fertilized": "All fertilized",
        "snooze": "Snooze 1 day",
    },
    "de": {
        "title": "PlantBased: Pflanzenpflege",
        "water": "Gießen fällig",
        "fertilize": "Düngen fällig",
        "all_watered": "Alle gewässert",
        "all_fertilized": "Alle gedüngt",
        "snooze": "1 Tag verschieben",
    },
}


def notification_texts(language: str) -> dict[str, str]:
    """Use HA's language, falling back to English for other locales."""
    return TEXTS.get(language.split("-")[0], TEXTS["en"])
